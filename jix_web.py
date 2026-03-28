import streamlit as st
from groq import Groq
import json
import os

# --- 1. CORE IDENTITY ---
ENGINEER = "Pathe"
OS_NAME = "JIX"

# --- 2. API CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 GROQ_API_KEY missing in Streamlit Secrets.")
    st.stop()

# --- 3. PRO-ULTRA UI (Modern Minimalist) ---
st.set_page_config(page_title=OS_NAME, page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    /* Global Background - Clean Neutral */
    .stApp {
        background-color: #ffffff;
        color: #202124;
    }
    
    /* Sidebar - Modern Slate */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Sidebar Text */
    section[data-testid="stSidebar"] .stText, section[data-testid="stSidebar"] label {
        color: #3c4043 !important;
    }

    /* Professional Message Bubbles */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Centering the Chat for that ChatGPT/Gemini look */
    .stChatMessageContent {
        font-size: 16px;
        line-height: 1.6;
        color: #3c4043;
    }

    /* The Chat Input - Fixed at Bottom & Styled */
    .stChatInputContainer {
        border-radius: 24px !important;
        border: 1px solid #dfe1e5 !important;
        background-color: white !important;
        box-shadow: 0 1px 6px rgba(32,33,36,.28) !important;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Title Styling */
    h1 {
        font-family: 'Google Sans', Arial, sans-serif;
        font-weight: 500;
        text-align: center;
        color: #1f1f1f;
        margin-top: 2rem !important;
    }

    /* Hide unnecessary Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGS (Memory) ---
if "chat_log" not in st.session_state:
    if os.path.exists("logs.json"):
        with open("logs.json", "r") as f:
            st.session_state.chat_log = json.load(f)
    else:
        st.session_state.chat_log = []

def save_logs():
    with open("logs.json", "w") as f:
        json.dump(st.session_state.chat_log, f)

# --- 5. SIDEBAR (Navigation & Identity) ---
with st.sidebar:
    st.title(f"🌐 {OS_NAME}")
    st.write(f"Account: **{ENGINEER}**")
    st.divider()
    
    # Simple Chat History List
    st.subheader("Recent")
    if st.session_state.chat_log:
        for msg in st.session_state.chat_log[-5:]: # Show last 5
            if msg["role"] == "user":
                st.caption(f"💬 {msg['content'][:25]}...")
    
    st.divider()
    if st.button("🗑️ Clear all chats", use_container_width=True):
        st.session_state.chat_log = []
        save_logs()
        st.rerun()

# --- 6. MAIN INTERFACE ---
st.title("Where should we start?")

# Wrap chat in a container to keep it centered
chat_container = st.container()

with chat_container:
    for message in st.session_state.chat_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask JIX..."):
    # Add user message
    st.session_state.chat_log.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            sys_msg = f"You are JIX, a world-class AI assistant developed for {ENGINEER}. Provide high-quality, professional, and insightful answers."
            history = [{"role": "system", "content": sys_msg}] + st.session_state.chat_log[-10:]
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history
            )
            
            reply = response.choices[0].message.content
            st.markdown(reply)
            
            st.session_state.chat_log.append({"role": "assistant", "content": reply})
            save_logs()
