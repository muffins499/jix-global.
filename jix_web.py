import streamlit as st
from groq import Groq
import json
import os

# --- 1. MEMORY & SETTINGS ---
CHATS_FILE = "jix_brain_v10.json"
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

if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_data(CHATS_FILE, {})
if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"
if "user_prefs" not in st.session_state:
    st.session_state.user_prefs = load_data(SETTINGS_FILE, {"user_name": "Pathe", "personality": "Strategic Advisor", "theme": "Light Blue"})

# --- 2. CSS FOR THE INTEGRATED "PILL" BAR ---
st.set_page_config(page_title="JIX GLOBAL", layout="wide")

themes = {
    "Light Blue": {"bg": "#ffffff", "text": "#202124", "sidebar": "#f8f9fa", "input_bg": "#f1f3f4"},
    "Dark Mode": {"bg": "#1f1f1f", "text": "#e8eaed", "sidebar": "#2d2e30", "input_bg": "#303134"}
}
t = themes.get(st.session_state.user_prefs["theme"], themes["Light Blue"])

st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {t['sidebar']} !important; }}
    
    /* The "Integrated Bar" Container */
    .integrated-bar {{
        background-color: {t['input_bg']};
        border-radius: 30px;
        padding: 5px 20px;
        display: flex;
        align-items: center;
        max-width: 850px;
        margin: 0 auto;
        border: 1px solid transparent;
    }}
    
    .integrated-bar:focus-within {{
        border: 1px solid #1a73e8;
        background-color: {t['bg']};
        box-shadow: 0 1px 6px rgba(32,33,36,.28);
    }}

    /* Hiding the default Streamlit input styling to blend it in */
    .stChatInputContainer {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }}
    
    /* Styling the Plus Popover to be small and clean */
    div[data-testid="stPopover"] button {{
        background-color: transparent !important;
        border: none !important;
        font-size: 20px !important;
        padding: 0 10px 0 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (Chats & Config) ---
with st.sidebar:
    st.title("🌐 JIX OS")
    tab1, tab2 = st.tabs(["💬 History", "⚙️ Config"])
    with tab1:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.active_title = "New Chat"
            st.rerun()
        st.divider()
        for title in list(st.session_state.all_chats.keys())[::-1]:
            if st.button(f"💬 {title[:20]}", key=title, use_container_width=True):
                st.session_state.active_title = title
                st.rerun()
    with tab2:
        st.session_state.user_prefs["user_name"] = st.text_input("Engineer", st.session_state.user_prefs["user_name"])
        st.session_state.user_prefs["theme"] = st.selectbox("UI", list(themes.keys()))
        if st.button("Save"):
            save_data(SETTINGS_FILE, st.session_state.user_prefs)
            st.rerun()

# --- 4. MAIN CHAT LOGIC ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.stop()

active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

# Display Messages
for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. THE INTEGRATED INPUT BAR (THE FIX) ---
st.write("---")
# Creating a horizontal layout for the Plus and the Input
input_wrapper = st.container()
with input_wrapper:
    col_plus, col_text = st.columns([0.07, 0.93])
    
    with col_plus:
        with st.popover("➕", help="Tools"):
            q_scale = st.button("🚀 Scale")
            q_code = st.button("📝 Code")
            q_trend = st.button("📊 Trends")

    with col_text:
        user_input = st.chat_input("Ask JIX...")

# --- 6. AI ENGINE ---
final_prompt = user_input
if q_scale: final_prompt = "Scale a business idea."
if q_code: final_prompt = "Draft a script."
if q_trend: final_prompt = "Current tech trends."

if final_prompt:
    if active_id == "New Chat":
        new_title = " ".join(final_prompt.split()[:3]) + "..."
        st.session_state.all_chats[new_title] = []
        st.session_state.active_title = new_title
        active_id = new_title

    st.session_state.all_chats[active_id].append({"role": "user", "content": final_prompt})
    
    with st.chat_message("assistant"):
        sys = f"You are JIX for {st.session_state.user_prefs['user_name']}."
        hist = [{"role": "system", "content": sys}] + st.session_state.all_chats[active_id][-10:]
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist)
        reply = res.choices[0].message.content
        st.markdown(reply)
        st.session_state.all_chats[active_id].append({"role": "assistant", "content": reply})
        save_data(CHATS_FILE, st.session_state.all_chats)
    st.rerun()
