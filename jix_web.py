import streamlit as st
from groq import Groq
import json
import os

# --- 1. CORE CONFIG ---
CHATS_FILE = "jix_brain_v7.json"
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
    st.session_state.user_prefs = load_data(SETTINGS_FILE, {"user_name": "Pathe", "personality": "Strategic Advisor", "theme": "Light Blue"})

# --- 2. UI & THEME ---
st.set_page_config(page_title="JIX GLOBAL", page_icon="🌐", layout="wide")

themes = {
    "Light Blue": {"bg": "#f0f4f8", "text": "#102a43", "sidebar": "#102a43"},
    "Dark Mode": {"bg": "#0e1117", "text": "#ffffff", "sidebar": "#161b22"}
}
t = themes.get(st.session_state.user_prefs.get("theme", "Light Blue"), themes["Light Blue"])

st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {t['sidebar']} !important; }}
    [data-testid="stChatMessage"] {{ max-width: 800px; margin: 0 auto; }}
    .stChatInputContainer {{ max-width: 800px; margin: 0 auto; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🌐 JIX OS")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()
    st.divider()
    for title in list(st.session_state.all_chats.keys())[::-1]:
        if st.button(f"💬 {title[:20]}", key=title, use_container_width=True):
            st.session_state.active_title = title
            st.rerun()

# --- 4. BRAIN CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY in Secrets!")
    st.stop()

# --- 5. MAIN CHAT ---
active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

# Show history
for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. INPUT & PLUS MENU ---
input_col, btn_col = st.columns([0.8, 0.2])
with btn_col:
    with st.popover("➕ Actions"):
        q_code = st.button("📝 Draft Code")
        q_trend = st.button("📊 Trends")

user_input = st.chat_input("Command JIX...")
final_prompt = user_input if user_input else ("Draft a Python script" if q_code else ("What are tech trends?" if q_trend else None))

if final_prompt:
    # Handle New Chat Titling
    if active_id == "New Chat":
        new_title = " ".join(final_prompt.split()[:3]) + "..."
        st.session_state.all_chats[new_title] = []
        st.session_state.active_title = new_title
        active_id = new_title

    # Add message and show immediately
    st.session_state.all_chats[active_id].append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # Generate Response
    with st.chat_message("assistant"):
        try:
            sys = f"You are JIX for {st.session_state.user_prefs['user_name']}. Style: {st.session_state.user_prefs['personality']}."
            hist = [{"role": "system", "content": sys}] + st.session_state.all_chats[active_id][-5:]
            
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist)
            ans = completion.choices[0].message.content
            st.markdown(ans)
            st.session_state.all_chats[active_id].append({"role": "assistant", "content": ans})
            
            # Save to disk
            save_data(CHATS_FILE, st.session_state.all_chats)
        except Exception as e:
            st.error(f"Neural Error: {e}")
    
    st.rerun()
