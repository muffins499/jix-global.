import streamlit as st
from groq import Groq
import json
import os

# --- 1. CORE IDENTITY ---
ENGINEER = "Pathe"
OS_NAME = "JIX GLOBAL"

# --- 2. API CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. PROFESSIONAL "SKY-LIGHT" UI ---
st.set_page_config(page_title=OS_NAME, page_icon="📡", layout="wide")

st.markdown("""
    <style>
    /* Clean Light Blue Gradient */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        color: #102a43;
    }
    
    /* Sidebar: Professional Deep Blue */
    section[data-testid="stSidebar"] {
        background-color: #102a43 !important;
        color: white !important;
    }
    
    /* Chat Bubbles: Clean White Glass */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid #bcccdc;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }

    /* Professional Headers */
    h1, h2, h3 {
        color: #243b53 !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }

    /* Input Box: Modern & Focused */
    .stChatInputContainer {
        border-radius: 10px !important;
        border: 1px solid #829ab1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. RELIABLE MEMORY ENGINE ---
# We use st.session_state first, then backup to file
if "chat_log" not in st.session_state:
    if os.path.exists("logs.json"):
        with open("logs.json", "r") as f:
            st.session_state.chat_log = json.load(f)
    else:
        st.session_state.chat_log = []

def save_logs():
    with open("logs.json", "w") as f:
        json.dump(st.session_state.chat_log, f)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("📡 JIX GLOBAL")
    st.write(f"Logged in: **{ENGINEER}**")
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_log = []
        save_logs()
        st.rerun()

# --- 6. CHAT INTERFACE ---
st.title("Neural Communication Link")

# Display logs immediately (this ensures you see them!)
for message in st.session_state.chat_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Command Entry
if prompt := st.chat_input("Command JIX..."):
    # Add user message to log
    st.session_state.chat_log.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            sys_msg = f"You are JIX, a professional AI assistant for Engineer {ENGINEER}. Be concise, smart, and helpful."
            
            # Keep history short for speed (last 10 messages)
            history = [{"role": "system", "content": sys_msg}] + st.session_state.chat_log[-10:]
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history
            )
            
            reply = response.choices[0].message.content
            st.markdown(reply)
            
            # Save to log and file
            st.session_state.chat_log.append({"role": "assistant", "content": reply})
            save_logs()
