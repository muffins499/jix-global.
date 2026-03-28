import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime, timedelta

# --- 1. PROACTIVE SEARCH ENGINE ---
def perform_search(query):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            # We use a broader search to ensure we get results
            results = list(ddgs.text(query, max_results=3))
            if results:
                return "\n\n".join([f"Source: {r['title']}\n{r['body']}" for r in results])
            return "No recent data found for this specific query."
    except Exception as e:
        return f"Neural Search Link interrupted. Error: {str(e)}"

# --- 2. DATA PERSISTENCE ---
CHATS_FILE = "jix_v1_history.json"
SETTINGS_FILE = "jix_v1_settings.json"

def load_json(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r") as f: return json.load(f)
    except: pass
    return default

if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_json(CHATS_FILE, {})
if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"
if "user_prefs" not in st.session_state:
    saved = load_json(SETTINGS_FILE, {})
    st.session_state.user_prefs = {"name": "Pathe", "country": "South Africa", **saved}

# --- 3. TIME LOGIC ---
TZ_MAP = {"South Africa": 2, "UK": 0, "USA (EST)": -5, "UAE": 4, "India": 5.5, "Nigeria": 1}
user_country = st.session_state.user_prefs.get("country", "South Africa")
offset = TZ_MAP.get(user_country, 2)
local_time = (datetime.utcnow() + timedelta(hours=offset)).strftime("%H:%M")

# --- 4. DESIGN (PROFESSIONAL GREY) ---
st.set_page_config(page_title="JIX GLOBAL", layout="wide")
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f1f3f4; color: #202124; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff !important; border-right: 1px solid #ddd; }}
    [data-testid="stChatMessage"] {{ background-color: #ffffff !important; border-radius: 15px; border: 1px solid #e0e0e0; max-width: 800px; margin: 0 auto 10px auto; }}
    .stChatInputContainer {{ max-width: 800px; margin: 0 auto; }}
    .stButton button {{ border-radius: 12px; background-color: white; border: 1px solid #ccc; transition: 0.3s; }}
    .stButton button:hover {{ border-color: #1a73e8; color: #1a73e8; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🌐 JIX OS")
    st.caption(f"📍 {user_country} | 🕒 {local_time}")
    if st.button("➕ New Session", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()
    st.divider()
    for title in list(st.session_state.all_chats.keys())[::-1]:
        if st.button(f"💬 {title[:22]}", key=title, use_container_width=True):
            st.session_state.active_title = title
            st.rerun()
    st.divider()
    with st.expander("⚙️ Settings"):
        st.session_state.user_prefs["name"] = st.text_input("User", st.session_state.user_prefs.get("name"))
        st.session_state.user_prefs["country"] = st.selectbox("Region", list(TZ_MAP.keys()))
        if st.button("Apply Changes"):
            with open(SETTINGS_FILE, "w") as f: json.dump(st.session_state.user_prefs, f)
            st.rerun()

# --- 6. MAIN CHAT ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

if not st.session_state.all_chats[active_id]:
    st.markdown(f"<h1 style='text-align: center; margin-top: 80px;'>Systems Online, {st.session_state.user_prefs['name']}.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5f6368;'>Select a module or type a command below.</p>", unsafe_allow_html=True)

for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. TOOLBAR ---
st.write("")
col1, col2, col3, _ = st.columns([1,1,1,5])
with col1: s_btn = st.button("🌐 Global Search")
with col2: c_btn = st.button("📝 Code Mode")
with col3: t_btn = st.button("📊 Market Trends")

user_input = st.chat_input("Enter command...")
final_prompt = user_input
search_query = None

# If user clicks search, we trigger a text input for the search topic
if s_btn:
    search_query = st.text_input("What should JIX research for you?", key="search_bar")

if search_query:
    with st.spinner("Accessing Live Data..."):
        context = perform_search(search_query)
        final_prompt = f"ACT AS A SEARCH ASSISTANT. Based on this live data: {context}\n\nAnswer this: {search_query}"

# Handle logic for other buttons
if c_btn: final_prompt = "Write a high-quality, documented Python automation script."
if t_btn: final_prompt = "What are the biggest tech and business trends for 2026?"

# --- 8. AI EXECUTION ---
if final_prompt:
    if active_id == "New Chat":
        active_id = final_prompt[:30].strip() + "..."
        st.session_state.all_chats[active_id] = []
        st.session_state.active_title = active_id

    st.session_state.all_chats[active_id].append({"role": "user", "content": final_prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("JIX Processing..."):
            sys = f"You are JIX OS. Strategic partner to {st.session_state.user_prefs['name']}."
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys}] + st.session_state.all_chats[active_id][-6:]
            )
            reply = res.choices[0].message.content
            st.markdown(reply)
            st.session_state.all_chats[active_id].append({"role": "assistant", "content": reply})
            with open(CHATS_FILE, "w") as f: json.dump(st.session_state.all_chats, f)
    st.rerun()
