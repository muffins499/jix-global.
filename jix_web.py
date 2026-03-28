import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime, timedelta

# --- 1. SEARCH ENGINE SAFETY CHECK ---
try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

# --- 2. CORE DATA & SETTINGS ---
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
    st.session_state.user_prefs = {"name": "Pathe", "country": "South Africa"}
    st.session_state.user_prefs.update(saved)

# --- 3. TIME ENGINE ---
TZ_MAP = {"South Africa": 2, "UK": 0, "USA (EST)": -5, "UAE": 4, "India": 5.5, "Nigeria": 1}
user_country = st.session_state.user_prefs.get("country", "South Africa")
offset = TZ_MAP.get(user_country, 2)
local_time = (datetime.utcnow() + timedelta(hours=offset)).strftime("%H:%M")

# --- 4. THE DESIGN ---
st.set_page_config(page_title="JIX GLOBAL", layout="wide")
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8f9fa; color: #202124; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff !important; border-right: 1px solid #dadce0; }}
    [data-testid="stChatMessage"] {{ background-color: #ffffff !important; border: 1px solid #dadce0; border-radius: 12px; max-width: 800px; margin: 0 auto 10px auto; }}
    .stChatInputContainer {{ max-width: 800px; margin: 0 auto; }}
    .stButton button {{ border-radius: 20px; border: 1px solid #dadce0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🌐 JIX OS")
    st.caption(f"📍 {user_country} | 🕒 {local_time}")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()
    st.divider()
    for title in list(st.session_state.all_chats.keys())[::-1]:
        if st.button(f"💬 {title[:20]}", key=title, use_container_width=True):
            st.session_state.active_title = title
            st.rerun()
    st.divider()
    with st.expander("⚙️ Settings"):
        st.session_state.user_prefs["name"] = st.text_input("Name", st.session_state.user_prefs.get("name", "Pathe"))
        st.session_state.user_prefs["country"] = st.selectbox("Location", list(TZ_MAP.keys()))
        if st.button("Save Settings"):
            with open(SETTINGS_FILE, "w") as f: json.dump(st.session_state.user_prefs, f)
            st.rerun()

# --- 6. CHAT LOGIC ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY to Secrets")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. SEARCH FUNCTION ---
def perform_search(query):
    if not SEARCH_AVAILABLE:
        return "Search is initializing. Please update requirements.txt and wait 1 minute."
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n\n".join(results)
    except Exception as e:
        return f"Search error: {e}"

# --- 8. TOOLBAR & INPUT ---
st.write("")
c1, c2, c3, _ = st.columns([1,1,1,5])
with c1: search_btn = st.button("🌐 Search")
with c2: code_btn = st.button("📝 Code")
with c3: trend_btn = st.button("📊 Trends")

user_input = st.chat_input("Message JIX...")
final_prompt = user_input

if search_btn:
    search_query = st.text_input("What should JIX research?")
    if search_query:
        with st.spinner("Searching..."):
            context = perform_search(search_query)
            final_prompt = f"Using this data: {context}, answer: {search_query}"

if final_prompt:
    if active_id == "New Chat":
        active_id = final_prompt[:25] + "..."
        st.session_state.all_chats[active_id] = []
        st.session_state.active_title = active_id

    st.session_state.all_chats[active_id].append({"role": "user", "content": final_prompt})
    with st.chat_message("assistant"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are JIX OS."}] + st.session_state.all_chats[active_id][-5:]
        )
        reply = res.choices[0].message.content
        st.markdown(reply)
        st.session_state.all_chats[active_id].append({"role": "assistant", "content": reply})
        with open(CHATS_FILE, "w") as f: json.dump(st.session_state.all_chats, f)
    st.rerun()
