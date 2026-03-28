import streamlit as st
from groq import Groq
import json
import os

# --- 1. DATA PERSISTENCE ---
CHATS_FILE = "jix_brain_v9.json"
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

# --- 2. LIGHTER UI & NESTED INPUT CSS ---
st.set_page_config(page_title="JIX GLOBAL", page_icon="🌐", layout="wide")

# Adjusted themes to be less "Heavy" (Lighter Sidebars)
themes = {
    "Light Blue": {"bg": "#ffffff", "text": "#202124", "sidebar": "#f8f9fa", "chat_bg": "#f1f3f4"},
    "Dark Mode": {"bg": "#1f1f1f", "text": "#e8eaed", "sidebar": "#2d2e30", "chat_bg": "#303134"}
}
t = themes.get(st.session_state.user_prefs["theme"], themes["Light Blue"])

st.markdown(f"""
    <style>
    /* Main App Background */
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    
    /* Sidebar - Lighter & Modern */
    section[data-testid="stSidebar"] {{ 
        background-color: {t['sidebar']} !important; 
        border-right: 1px solid #ddd;
    }}
    
    /* Chat Bubbles */
    [data-testid="stChatMessage"] {{ 
        max-width: 800px; 
        margin: 0 auto 10px auto; 
        background-color: {t['chat_bg']} !important; 
        border-radius: 20px;
    }}

    /* Nested Plus Icon Trick */
    .stChatInputContainer {{
        padding-left: 50px !important; /* Make room for the plus */
    }}
    
    .floating-plus {{
        position: fixed;
        bottom: 42px;
        left: calc(50% - 390px); /* Aligns with the 800px wide input */
        z-index: 1000;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (History & Config) ---
with st.sidebar:
    st.title("🌐 JIX OS")
    st.caption(f"Engineer: {st.session_state.user_prefs['user_name']}")
    
    tab_chat, tab_set = st.tabs(["💬 Chats", "⚙️ Config"])
    
    with tab_chat:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.active_title = "New Chat"
            st.rerun()
        st.divider()
        for title in list(st.session_state.all_chats.keys())[::-1]:
            if st.button(f"💬 {title[:22]}", key=title, use_container_width=True):
                st.session_state.active_title = title
                st.rerun()

    with tab_set:
        st.subheader("Neural Identity")
        st.session_state.user_prefs["user_name"] = st.text_input("Engineer Name", st.session_state.user_prefs["user_name"])
        st.session_state.user_prefs["personality"] = st.selectbox("Tone", ["Strategic Advisor", "Sarcastic Genius", "Technical Expert"])
        st.session_state.user_prefs["theme"] = st.selectbox("UI Theme", list(themes.keys()))
        if st.button("💾 Save Settings", use_container_width=True):
            save_data(SETTINGS_FILE, st.session_state.user_prefs)
            st.rerun()

# --- 4. BRAIN CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY in Secrets!")
    st.stop()

# --- 5. CHAT DISPLAY ---
active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

if not st.session_state.all_chats[active_id]:
    st.markdown(f"<h1 style='text-align: center; margin-top: 150px; font-weight: 400;'>Where should we begin, {st.session_state.user_prefs['user_name']}?</h1>", unsafe_allow_html=True)

for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. THE NESTED PLUS MENU ---
# We wrap the popover in a div with our 'floating-plus' class
st.markdown('<div class="floating-plus">', unsafe_allow_html=True)
with st.popover("➕"):
    st.markdown("**Global Actions**")
    q_scale = st.button("🚀 Scale Idea", use_container_width=True)
    q_code = st.button("📝 Draft Code", use_container_width=True)
    q_trend = st.button("📊 Tech Trends", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Main input box
user_input = st.chat_input("Ask JIX...")

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
        with st.spinner("Processing..."):
            sys_msg = f"You are JIX for {st.session_state.user_prefs['user_name']}. Tone: {st.session_state.user_prefs['personality']}."
            hist = [{"role": "system", "content": sys_msg}] + st.session_state.all_chats[active_id][-10:]
            
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist)
            reply = res.choices[0].message.content
            st.markdown(reply)
            st.session_state.all_chats[active_id].append({"role": "assistant", "content": reply})
            save_data(CHATS_FILE, st.session_state.all_chats)
    
    st.rerun()
