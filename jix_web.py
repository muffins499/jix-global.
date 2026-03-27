import streamlit as st
from groq import Groq
from datetime import datetime

# --- 1. SYSTEM GATE ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Add it to Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="JIX GLOBAL OS", page_icon="📐", layout="wide")

# --- 2. INTELLIGENCE STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Neural Link"

# --- 3. THE INITIALIZATION (Sign-up) ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>📐 JIX GLOBAL</h1>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        user_id = st.text_input("Operator ID")
        lang = st.selectbox("Language", ["English", "Spanish", "French", "German", "Arabic", "Chinese", "Japanese"])
        if st.button("INITIALIZE SYSTEM"):
            st.session_state.authenticated = True
            st.session_state.user_name = user_id.split('@')[0].capitalize()
            st.session_state.language = lang
            st.rerun()
    st.stop()

# --- 4. SIDEBAR (History Management) ---
with st.sidebar:
    st.title("📐 JIX OS")
    if st.button("+ New Neural Link"):
        st.session_state.current_chat = f"Link {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[st.session_state.current_chat] = []
        st.rerun()

    st.divider()
    for title in st.session_state.chat_sessions.keys():
        if st.button(title, use_container_width=True):
            st.session_state.current_chat = title
            st.rerun()

# --- 5. THE BRAIN (Memory & Proactive Logic) ---
chat_name = st.session_state.current_chat
if chat_name not in st.session_state.chat_sessions:
    st.session_state.chat_sessions[chat_name] = []

# Display History
for msg in st.session_state.chat_sessions[chat_name]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
prompt = st.chat_input("Input command...")

if prompt:
    # 1. Add User message to memory
    st.session_state.chat_sessions[chat_name].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant", avatar="📐"):
        # 2. PROMPT ENGINEERING (The "Smart" Sauce)
        # We tell JIX it's an idea generator, not just a replier.
        system_instructions = (
            f"You are JIX GLOBAL, a hyper-intelligent AI OS created by Pathe. "
            f"Your language is {st.session_state.language}. "
            "You have full memory of this conversation. "
            "CRITICAL: Do not just answer. Give 3 creative 'Global Ideas' or 'Next Steps' "
            "at the end of every response to help Pathe expand his vision."
        )

        # 3. CONTEXT INJECTION (Sending the whole history for memory)
        full_context = [{"role": "system", "content": system_instructions}]
        full_context.extend(st.session_state.chat_sessions[chat_name])

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_context,
            temperature=0.8  # Higher temp = more creative ideas
        )

        ans = response.choices[0].message.content
        st.markdown(ans)
        st.session_state.chat_sessions[chat_name].append({"role": "assistant", "content": ans})