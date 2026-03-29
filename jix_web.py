import streamlit as st
import json
import os

# --- 1. THE GEMINI-INSPIRED CSS ---
st.set_page_config(page_title="JIX OS", page_icon="🌐", layout="wide")

st.markdown("""
<style>
    /* Clean, Light Background */
    .stApp { background-color: #ffffff; color: #1f1f1f; }
    
    /* Minimalist Sidebar */
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e3e3e3; }
    
    /* The "Pill" Input Bar Styling */
    .stChatInputContainer {
        padding: 10px !important;
        background: transparent !important;
    }
    .stChatInputContainer > div {
        border-radius: 32px !important;
        border: 1px solid #dfe1e5 !important;
        background-color: #ffffff !important;
        box-shadow: none !important;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Removing the clunky default buttons from the center */
    .centered-header { text-align: center; margin-top: 100px; color: #1f1f1f; }
    .sub-text { text-align: center; color: #70757a; margin-bottom: 40px; }

    /* Custom 'X' button for sidebar */
    .close-btn { color: #5f6368; cursor: pointer; float: right; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & DATA PERSISTENCE ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "New Session"

# --- 3. SIDEBAR (With 'X' Delete) ---
with st.sidebar:
    st.markdown("### 🌐 JIX OS")
    if st.button("➕ New Session", use_container_width=True):
        st.session_state.active_chat = "New Session"
        st.rerun()
    
    st.write("")
    st.caption("RECENT INTELLIGENCE")
    
    for title in list(st.session_state.all_chats.keys()):
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            if st.button(f"💬 {title[:18]}", key=f"s_{title}", use_container_width=True):
                st.session_state.active_chat = title
                st.rerun()
        with cols[1]:
            if st.button("✕", key=f"x_{title}", help="Close this session"):
                del st.session_state.all_chats[title]
                st.session_state.active_chat = "New Session"
                st.rerun()

# --- 4. MAIN INTERFACE ---
active_id = st.session_state.active_chat

if not st.session_state.all_chats.get(active_id):
    st.markdown("<h1 class='centered-header'>Systems Online, Pathe.</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>Search the web, write code, or analyze trends below.</p>", unsafe_allow_html=True)
else:
    for msg in st.session_state.all_chats[active_id]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. THE INTEGRATED TOOLBAR (THE '+' MENU) ---
# This replaces those 3 big buttons with a clean Gemini-style footer
footer_col1, footer_col2 = st.columns([0.1, 0.9])

with footer_col1:
    # This is your new "Integrated Plus" menu
    with st.popover("➕", help="Tools"):
        st.markdown("**Intelligence Modules**")
        if st.button("🌐 Global Search"): st.session_state.mode = "search"
        if st.button("📝 Code Mode"): st.session_state.mode = "code"
        if st.button("📊 Market Trends"): st.session_state.mode = "trends"

with footer_col2:
    user_input = st.chat_input("Enter command...")

# --- 6. EXECUTION ---
if user_input:
    if active_id == "New Session":
        # Rename session based on first input
        new_id = user_input[:25] + "..."
        st.session_state.all_chats[new_id] = []
        st.session_state.active_chat = new_id
        active_id = new_id
    
    st.session_state.all_chats[active_id].append({"role": "user", "content": user_input})
    
    # Simulate Response (Add your Groq call here)
    response = f"JIX processing: '{user_input}'"
    st.session_state.all_chats[active_id].append({"role": "assistant", "content": response})
    st.rerun()
