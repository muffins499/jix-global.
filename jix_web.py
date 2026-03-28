import streamlit as st
from groq import Groq
import json
import os

# --- 1. IDENTITY ---
ENGINEER = "Pathe"
OS_NAME = "JIX"

# --- 2. API CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 API Key Missing.")
    st.stop()

# --- 3. THE DESIGN (Gemini-Inspired) ---
st.set_page_config(page_title=OS_NAME, page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #202124; }
    section[data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e0e0e0; }
    [data-testid="stChatMessage"] { max-width: 800px; margin: 0 auto; background-color: transparent !important; border: none !important; }
    .stChatInputContainer { max-width: 800px; margin: 0 auto; border-radius: 28px !important; border: 1px solid #dfe1e5 !important; }
    h1 { text-align: center; font-family: 'Google Sans', sans-serif; font-weight: 400; color: #1f1f1f; margin-top: 50px; }
    .stButton button { border: none !important; background-color: transparent !important; text-align: left !important; padding: 10px !important; width: 100%; color: #3c4043 !important; }
    .stButton button:hover { background-color: #e8eaed !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. THE TITLE-BASED MEMORY ENGINE ---
def load_all_chats():
    if os.path.exists("jix_brain.json"):
        with open("jix_brain.json", "r") as f: return json.load(f)
    return {}

def save_all_chats(chats):
    with open("jix_brain.json", "w") as f: json.dump(chats, f)

if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_all_chats()

if "active_title" not in st.session_state:
    if st.session_state.all_chats:
        st.session_state.active_title = list(st.session_state.all_chats.keys())[0]
    else:
        st.session_state.active_title = "New Chat"

# --- 5. SIDEBAR (The Chat Title List) ---
with st.sidebar:
    st.title(f"🌐 {OS_NAME}")
    
    if st.button("➕ New chat", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()
    
    st.divider()
    st.subheader("Recent")
    
    # List actual titles in sidebar
    for title in reversed(list(st.session_state.all_chats.keys())):
        if st.button(f"💬 {title}", key=title):
            st.session_state.active_title = title
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear all history"):
        st.session_state.all_chats = {}
        st.session_state.active_title = "New Chat"
        save_all_chats({})
        st.rerun()

# --- 6. MAIN INTERFACE ---
active_title = st.session_state.active_title

# If the chat exists, show messages. If not, show the greeting.
if active_title in st.session_state.all_chats:
    st.title(active_title)
    for msg in st.session_state.all_chats[active_title]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
else:
    st.title("Where should we start?")

# --- 7. INPUT & DYNAMIC TITLING ---
if prompt := st.chat_input("Ask JIX..."):
    
    current_messages = st.session_state.all_chats.get(active_title, [])
    
    # Add User Message
    current_messages.append({"role": "user", "content": prompt})
    
    # If this is the start of a "New Chat", generate a real title
    target_title = active_title
    if active_title == "New Chat":
        # Create a title from the first 5 words
        new_title = " ".join(prompt.split()[:5])
        if len(prompt.split()) > 5: new_title += "..."
        
        # Ensure title is unique
        if new_title in st.session_state.all_chats:
            new_title += f" ({len(st.session_state.all_chats)})"
            
        st.session_state.all_chats[new_title] = current_messages
        st.session_state.active_title = new_title
        target_title = new_title
    else:
        st.session_state.all_chats[active_title] = current_messages

    # Display immediately
    st.rerun() # Refresh to show user message and new sidebar title

    # Generate AI Response (This will happen after the rerun if we structure it for speed)
    # Note: For even better performance, I'll place the AI call inside the block above
