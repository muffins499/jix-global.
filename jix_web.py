import streamlit as st
from groq import Groq
import json
import os

# --- 1. SETTINGS & BRAIN CONFIG ---
# Ensure your Groq Key is in your Streamlit Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Groq API Key not found. Please add it to your Secrets.")

CHATS_FILE = "jix_master_history.json"

# --- 2. THE "GEMINI" PREMIUM UI (CSS) ---
st.set_page_config(page_title="JIX OS", page_icon="🌐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #1f1f1f; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e3e3e3; }
    
    /* The Floating Pill Input */
    .stChatInputContainer { padding: 20px !important; background: transparent !important; }
    .stChatInputContainer > div {
        border-radius: 32px !important;
        border: 1px solid #dfe1e5 !important;
        background-color: #ffffff !important;
        max-width: 800px;
        margin: 0 auto;
        box-shadow: 0 1px 6px rgba(32,33,36,0.1) !important;
    }

    /* Message Styling */
    [data-testid="stChatMessage"] { max-width: 800px; margin: 0 auto; border: none !important; }
    
    /* Modern Sidebar Buttons */
    .stButton button { border-radius: 10px; border: none; }
    .stButton button:hover { background-color: #e8f0fe; color: #1a73e8; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION & HISTORY PERSISTENCE (Clean Version) ---
if "all_chats" not in st.session_state:
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, "r") as f:
            st.session_state.all_chats = json.load(f)
    else:
        st.session_state.all_chats = {}

# Ensure we always have an active chat, but don't force it into the saved dict yet
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "New Session"

# --- 4. SIDEBAR (The "X" Logic + Duplicate Fix) ---
with st.sidebar:
    st.markdown("# **JIX OS**")
    if st.button("➕ New Session", use_container_width=True):
        st.session_state.active_chat = "New Session"
        st.rerun()
    
    st.divider()
    st.caption("RECENT INTELLIGENCE")
    
    # Only show chats that actually have content
    for title in list(st.session_state.all_chats.keys()):
        # skip empty ghost sessions
        if not st.session_state.all_chats[title]:
            continue
            
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            if st.button(f"💬 {title[:18]}", key=f"sel_{title}", use_container_width=True):
                st.session_state.active_chat = title
                st.rerun()
        with cols[1]:
            if st.button("✕", key=f"del_{title}", help="Close Session"):
                del st.session_state.all_chats[title]
                with open(CHATS_FILE, "w") as f:
                    json.dump(st.session_state.all_chats, f)
                st.session_state.active_chat = "New Session"
                st.rerun()
# --- 5. MAIN INTERFACE ---
active_id = st.session_state.active_chat
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

# Welcome screen if chat is empty
if not st.session_state.all_chats[active_id]:
    st.markdown("<br><br><h1 style='text-align:center;'>Systems Online, Pathe.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#70757a;'>Enter a command to begin strategic analysis.</p>", unsafe_allow_html=True)

# Display Messages
for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. FLOATING INPUT & TOOLS ---
col_plus, col_input = st.columns([0.1, 0.9])
with col_plus:
    with st.popover("➕"):
        st.markdown("**Modules**")
        st.button("📡 Live Search")
        st.button("📝 Code Architect")

with col_input:
    user_input = st.chat_input("Command JIX...")

# --- 7. THE BRAIN (GROQ REAL-TIME EXECUTION) ---
if user_input:
    # Handle auto-naming for new sessions
    current_title = active_id
    if active_id == "New Session":
        current_title = user_input[:25].strip()
        st.session_state.all_chats[current_title] = []
        st.session_state.active_chat = current_title

    # Add User Message
    st.session_state.all_chats[current_title].append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        response_area = st.empty()
        full_ai_response = ""
        
        # Call Groq (No more placeholders!)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are JIX OS, a high-level strategic AI. Be brilliant and concise."}
            ] + st.session_state.all_chats[current_title],
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_ai_response += chunk.choices[0].delta.content
                response_area.markdown(full_ai_response + "▌")
        
        response_area.markdown(full_ai_response)
        
        # Add Assistant Message to history
        st.session_state.all_chats[current_title].append({"role": "assistant", "content": full_ai_response})
    
    # Save everything to the file
    with open(CHATS_FILE, "w") as f:
        json.dump(st.session_state.all_chats, f)
    
    st.rerun()
    
