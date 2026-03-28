import streamlit as st
from groq import Groq
import json
import os

# --- 1. MEMORY & SETTINGS ENGINE ---
CHATS_FILE = "jix_brain_v8.json"
SETTINGS_FILE = "jix_settings.json"

def load_data(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r") as f: return json.load(f)
    except: pass
    return default

def save_data(file, data):
    try:
        with open(file, "w") as f: json.dump(data, f)
    except: pass

# Initialize Session States
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_data(CHATS_FILE, {})
if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"
if "user_prefs" not in st.session_state:
    st.session_state.user_prefs = load_data(SETTINGS_FILE, {
        "user_name": "Pathe", 
        "personality": "Strategic Advisor", 
        "theme": "Light Blue"
    })

# --- 2. UI THEMING ---
st.set_page_config(page_title="JIX GLOBAL", page_icon="🌐", layout="wide")

themes = {
    "Light Blue": {"bg": "#f0f4f8", "text": "#102a43", "sidebar": "#102a43", "chat_bg": "#ffffff"},
    "Dark Mode": {"bg": "#0e1117", "text": "#ffffff", "sidebar": "#161b22", "chat_bg": "#262730"}
}
t = themes.get(st.session_state.user_prefs["theme"], themes["Light Blue"])

st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {t['sidebar']} !important; }}
    [data-testid="stChatMessage"] {{ max-width: 850px; margin: 0 auto; background-color: {t['chat_bg']} !important; border-radius: 15px; }}
    /* Styling the input area to look professional */
    .stChatInputContainer {{ max-width: 850px; margin: 0 auto; }}
    .stButton button {{ border-radius: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (RESTORED SETTINGS & HELP) ---
with st.sidebar:
    st.title("🌐 JIX OS")
    tab_chat, tab_set, tab_help = st.tabs(["💬 Chats", "⚙️ Config", "❓ Help"])
    
    with tab_chat:
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.active_title = "New Chat"
            st.rerun()
        st.divider()
        for title in list(st.session_state.all_chats.keys())[::-1]:
            if st.button(f"💬 {title[:20]}", key=title, use_container_width=True):
                st.session_state.active_title = title
                st.rerun()

    with tab_set:
        st.subheader("Neural Identity")
        st.session_state.user_prefs["user_name"] = st.text_input("Engineer Name", st.session_state.user_prefs["user_name"])
        st.session_state.user_prefs["personality"] = st.selectbox("Tone", ["Strategic Advisor", "Sarcastic Genius", "Technical Expert"])
        st.session_state.user_prefs["theme"] = st.selectbox("UI Theme", list(themes.keys()))
        if st.button("💾 Save Settings"):
            save_data(SETTINGS_FILE, st.session_state.user_prefs)
            st.rerun()

    with tab_help:
        st.write("JIX v2.1-Stable")
        st.caption("Developed for Engineer Pathe")

# --- 4. BRAIN CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY in Secrets!")
    st.stop()

# --- 5. MAIN INTERFACE ---
active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

if not st.session_state.all_chats[active_id]:
    st.markdown("<h1 style='text-align: center; margin-top: 100px;'>How can I help you today?</h1>", unsafe_allow_html=True)
else:
    st.markdown(f"<p style='text-align: center; color: gray;'>{active_id}</p>", unsafe_allow_html=True)

for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. THE "PLUS" INPUT BAR (LEFT SIDE) ---
st.divider()
# Use columns to put the Plus button on the LEFT
plus_col, input_col = st.columns([0.1, 0.9])

with plus_col:
    with st.popover("➕"):
        st.markdown("**Global Actions**")
        q_scale = st.button("🚀 Scale Idea")
        q_code = st.button("📝 Draft Code")
        q_trend = st.button("📊 Tech Trends")

with input_col:
    user_input = st.chat_input("Command JIX...")

# Action Logic
final_prompt = user_input
if q_scale: final_prompt = "Give me a high-level strategy to scale a new business idea."
if q_code: final_prompt = "Draft a professional Python script for an automation module."
if q_trend: final_prompt = "What are the top global tech trends for 2026?"

if final_prompt:
    if active_id == "New Chat":
        new_title = " ".join(final_prompt.split()[:4]) + "..."
        st.session_state.all_chats[new_title] = []
        st.session_state.active_title = new_title
        active_id = new_title

    st.session_state.all_chats[active_id].append({"role": "user", "content": final_prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            sys_msg = f"You are JIX for {st.session_state.user_prefs['user_name']}. Personality: {st.session_state.user_prefs['personality']}."
            hist = [{"role": "system", "content": sys_msg}] + st.session_state.all_chats[active_id][-10:]
            
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist)
            reply = res.choices[0].message.content
            st.markdown(reply)
            st.session_state.all_chats[active_id].append({"role": "assistant", "content": reply})
            save_data(CHATS_FILE, st.session_state.all_chats)
    
    st.rerun()
