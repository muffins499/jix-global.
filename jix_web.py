import streamlit as st
from groq import Groq
import json
import os

# --- 1. CORE CONFIG & PERSISTENCE ---
SETTINGS_FILE = "jix_settings.json"
CHATS_FILE = "jix_brain_v5.json"

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f: return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

# Initialize Session States
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_json(CHATS_FILE, {})
if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"
if "user_prefs" not in st.session_state:
    st.session_state.user_prefs = load_json(SETTINGS_FILE, {
        "user_name": "Pathe",
        "personality": "Strategic Advisor",
        "theme": "Light Blue"
    })

# --- 2. THE DESIGN ENGINE (Dynamic Themes) ---
st.set_page_config(page_title="JIX GLOBAL", page_icon="🌐", layout="wide")

# Map user choice to CSS
theme_colors = {
    "Light Blue": {"bg": "#f0f4f8", "text": "#102a43", "chat": "#ffffff"},
    "Dark Mode": {"bg": "#0e1117", "text": "#ffffff", "chat": "#262730"},
    "Neon Matrix": {"bg": "#000000", "text": "#00ff41", "chat": "#0a0a0a"}
}
c = theme_colors.get(st.session_state.user_prefs["theme"])

st.markdown(f"""
    <style>
    .stApp {{ background-color: {c['bg']}; color: {c['text']}; }}
    [data-testid="stChatMessage"] {{ background-color: {c['chat']} !important; border-radius: 15px; border: 1px solid #e0e0e0; }}
    .stChatInputContainer {{ max-width: 800px; margin: 0 auto; border-radius: 30px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (Settings & History) ---
with st.sidebar:
    st.title("🌐 JIX CONTROL")
    
    # NEW: Settings & Help Tabs
    tab1, tab2, tab3 = st.tabs(["💬 History", "⚙️ Settings", "❓ Help"])
    
    with tab1:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.active_title = "New Chat"
            st.rerun()
        st.divider()
        for title in reversed(list(st.session_state.all_chats.keys())):
            if st.button(f"💬 {title}", key=title, use_container_width=True):
                st.session_state.active_title = title
                st.rerun()

    with tab2:
        st.subheader("Neural Identity")
        st.session_state.user_prefs["user_name"] = st.text_input("Lead Engineer Name", st.session_state.user_prefs["user_name"])
        st.session_state.user_prefs["personality"] = st.selectbox("AI Personality", ["Strategic Advisor", "Tech Support", "Sarcastic Genius", "Creative Partner"])
        st.session_state.user_prefs["theme"] = st.selectbox("UI Theme", list(theme_colors.keys()))
        
        if st.button("💾 Save Preferences"):
            save_json(SETTINGS_FILE, st.session_state.user_prefs)
            st.success("Preferences Locked.")
            st.rerun()

    with tab3:
        st.markdown("""
        **Commands:**
        - `/reset`: Wipes the current chat.
        - `/title [name]`: Renames this chat.
        - **Pro-tip:** Use Settings to change my tone!
        """)

# --- 4. THE BRAIN (Now with Identity Memory) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 API Key Missing.")
    st.stop()

active_title = st.session_state.active_title
st.title(active_title if active_title != "New Chat" else "How can I help you today?")

# Show History
current_msgs = st.session_state.all_chats.get(active_title, [])
for m in current_msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# User Input
if prompt := st.chat_input(f"Command JIX, {st.session_state.user_prefs['user_name']}..."):
    # Identity Prompt Injection
    sys_msg = (
        f"You are JIX GLOBAL OS. Your lead engineer is {st.session_state.user_prefs['user_name']}. "
        f"Adopt the personality of a {st.session_state.user_prefs['personality']}. "
        "Remember all past details discussed in this conversation."
    )
    
    # Logic to handle new chat naming
    if active_title == "New Chat":
        active_title = " ".join(prompt.split()[:4])
        st.session_state.active_title = active_title
        st.session_state.all_chats[active_title] = []
    
    # 1. User Message
    st.session_state.all_chats[active_title].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # 2. AI Response
    with st.chat_message("assistant"):
        hist = [{"role": "system", "content": sys_msg}] + st.session_state.all_chats[active_title][-10:]
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist)
        reply = res.choices[0].message.content
        st.markdown(reply)
        st.session_state.all_chats[active_title].append({"role": "assistant", "content": reply})

    save_json(CHATS_FILE, st.session_state.all_chats)
    st.rerun()
