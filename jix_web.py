import streamlit as st
from groq import Groq
import json
import os

# --- 1. CORE CONFIG & PERSISTENCE ---
SETTINGS_FILE = "jix_settings.json"
CHATS_FILE = "jix_brain_v6.json"


def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)


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

# --- 2. THE DESIGN ENGINE (Pro UI) ---
st.set_page_config(page_title="JIX GLOBAL", page_icon="🌐", layout="wide")

theme_colors = {
    "Light Blue": {"bg": "#f0f4f8", "text": "#102a43", "chat": "#ffffff", "sidebar": "#102a43"},
    "Dark Mode": {"bg": "#0e1117", "text": "#ffffff", "chat": "#262730", "sidebar": "#161b22"},
    "Neon Matrix": {"bg": "#000000", "text": "#00ff41", "chat": "#0a0a0a", "sidebar": "#000000"}
}
c = theme_colors.get(st.session_state.user_prefs["theme"])

st.markdown(f"""
    <style>
    .stApp {{ background-color: {c['bg']}; color: {c['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {c['sidebar']} !important; }}
    [data-testid="stChatMessage"] {{ 
        background-color: {c['chat']} !important; 
        border-radius: 15px; 
        border: 1px solid #e0e0e0;
        max-width: 850px;
        margin: 0 auto 15px auto;
    }}
    .stChatInputContainer {{ max-width: 850px; margin: 0 auto; border-radius: 30px !important; }}
    h1, h2, h3 {{ font-family: 'Inter', sans-serif; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (History & Settings) ---
with st.sidebar:
    st.title("🌐 JIX OS")
    tab1, tab2, tab3 = st.tabs(["💬 Chats", "⚙️ Config", "❓ Help"])

    with tab1:
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.active_title = "New Chat"
            st.rerun()
        st.divider()
        for title in reversed(list(st.session_state.all_chats.keys())):
            if st.button(f"💬 {title[:20]}...", key=title, use_container_width=True):
                st.session_state.active_title = title
                st.rerun()

    with tab2:
        st.subheader("Neural Identity")
        st.session_state.user_prefs["user_name"] = st.text_input("User Name", st.session_state.user_prefs["user_name"])
        st.session_state.user_prefs["personality"] = st.selectbox("Tone", ["Strategic Advisor", "Sarcastic Genius",
                                                                           "Creative Partner"])
        st.session_state.user_prefs["theme"] = st.selectbox("UI Style", list(theme_colors.keys()))
        if st.button("💾 Save & Apply"):
            save_json(SETTINGS_FILE, st.session_state.user_prefs)
            st.rerun()

    with tab3:
        st.info("JIX is a Global OS designed for high-level strategy and technical drafting.")

# --- 4. API CONNECTION ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 Access Denied: Please add GROQ_API_KEY to Secrets.")
    st.stop()

# --- 5. MAIN INTERFACE ---
active_id = st.session_state.active_title
active_chat_msgs = st.session_state.all_chats.get(active_id, [])

if not active_chat_msgs:
    st.markdown("<h1 style='margin-top: 100px;'>How can I help you today?</h1>", unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='color: gray;'>{active_id}</h3>", unsafe_allow_html=True)

# Display Messages
for msg in active_chat_msgs:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. THE PLUS (+) POWER MENU & INPUT ---
st.divider()
input_col, btn_col = st.columns([0.85, 0.15])

with btn_col:
    with st.popover("➕", help="Global Actions"):
        st.markdown("**Quick Actions**")
        q_scale = st.button("🚀 Scale Idea", use_container_width=True)
        q_code = st.button("📝 Draft Code", use_container_width=True)
        q_trend = st.button("📊 Tech Trends", use_container_width=True)

with input_col:
    user_input = st.chat_input("Command JIX...")

# --- 7. PROCESSING ENGINE ---
final_prompt = None
if user_input:
    final_prompt = user_input
