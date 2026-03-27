import streamlit as st
from groq import Groq
import time
from datetime import datetime

# --- 1. CONFIG & API ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Please add your Groq key to .streamlit/secrets.toml")
    st.stop()

st.set_page_config(page_title="JIX GLOBAL", page_icon="📐", layout="wide")

# --- 2. SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"
if "project_map" not in st.session_state:
    st.session_state.project_map = {}
if "mode" not in st.session_state:
    st.session_state.mode = "Fast"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "mood" not in st.session_state:
    st.session_state.mood = "Professional"


# --- 3. SMART TITLE GENERATOR ---
def generate_short_title(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Create a 2-3 word title for this chat. No punctuation."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip().replace('"', '')
    except:
        return text[:15] + "..."


# --- 4. GLOBAL LOGIN GATE ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; margin-top: 5vh;'>📐 JIX GLOBAL OS</h1>", unsafe_allow_html=True)
    with st.container():
        _, mid, _ = st.columns([1, 1.5, 1])
        with mid:
            # Expanded International List
            all_languages = [
                "English", "Spanish", "French", "German", "Chinese",
                "Japanese", "Korean", "Arabic", "Portuguese", "Russian",
                "Italian", "Hindi", "Turkish", "Dutch", "Greek", "Hebrew"
            ]

            user_id = st.text_input("Operator ID (Email)")
            selected_lang = st.selectbox("Select System Language", all_languages)

            if st.button("🚀 INITIALIZE GLOBAL LINK", use_container_width=True):
                if "@" in user_id:
                    st.session_state.authenticated = True
                    st.session_state.user_name = user_id.split('@')[0].capitalize()
                    st.session_state.language = selected_lang
                    st.rerun()
                else:
                    st.warning("Please enter a valid Operator ID.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"### 📐 JIX GLOBAL")
    st.caption(f"🌐 {st.session_state.language} Interface")

    if st.button("📝 New chat", use_container_width=True):
        st.session_state.current_chat = "New Chat"
        st.rerun()

    st.divider()

    with st.expander("🎭 AI Mood Settings"):
        st.session_state.mood = st.select_slider(
            "Current Mood",
            options=["Serious", "Professional", "Friendly", "Creative", "Chaos"],
            value=st.session_state.mood
        )

    with st.expander("⭐ My stuff", expanded=True):
        if not st.session_state.project_map:
            st.caption("No projects pinned.")
        for proj, chat_ref in st.session_state.project_map.items():
            if st.button(f"📁 {proj}", key=f"p_{proj}", use_container_width=True):
                st.session_state.current_chat = chat_ref
                st.rerun()

    st.divider()
    st.caption("Recent History")
    # THE FIXED LOOP
    for title in reversed(list(st.session_state.chat_sessions.keys())):
        btn_type = "primary" if title == st.session_state.current_chat else "secondary"
        if st.button(f"💬 {title}", key=f"btn_{title}", type=btn_type, use_container_width=True):
            st.session_state.current_chat = title
            st.rerun()

# --- 6. HOME SCREEN ---
current_history = st.session_state.chat_sessions.get(st.session_state.current_chat, [])

if not current_history:
    st.markdown(f"""
        <div style="text-align: center; margin-top: 10vh;">
            <h1 style="font-size: 3.5rem;">📐 **Welcome, {st.session_state.user_name}**</h1>
            <h2 style="color: #888; font-weight: 400;">System ready in {st.session_state.language}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.write(" ")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.button("📝 Write", use_container_width=True)
    with c2: st.button("💡 Ideas", use_container_width=True)
    with c3: st.button("🎓 Learn", use_container_width=True)
    with c4: st.button("🚀 Boost", use_container_width=True)

# --- 7. MESSAGE DISPLAY ---
for msg in current_history:
    with st.chat_message(msg["role"], avatar="📐" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# --- 8. INPUT BAR ---
in_col, tool_col = st.columns([0.92, 0.08])
with tool_col:
    with st.popover("➕"):
        if st.button("🧠 Deep"): st.session_state.mode = "Deep"
        if st.button("⚡ Fast"): st.session_state.mode = "Fast"
        st.divider()
        if st.button("📌 Pin Project"):
            if st.session_state.current_chat != "New Chat":
                st.session_state.project_map[st.session_state.current_chat] = st.session_state.current_chat
                st.toast("Project Saved!")

with in_col:
    prompt = st.chat_input(f"Syncing in {st.session_state.language}...")

# --- 9. THE BRAIN ---
if prompt:
    active_chat = st.session_state.current_chat
    if active_chat == "New Chat":
        new_title = generate_short_title(prompt)
        st.session_state.chat_sessions[new_title] = []
        st.session_state.current_chat = new_title
        active_chat = new_title

    st.session_state.chat_sessions[active_chat].append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="📐"):
        with st.spinner("Thinking..."):
            try:
                sys_content = f"You are JIX GLOBAL AI. You MUST respond in {st.session_state.language} language. Tone: {st.session_state.mood}."
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_content}, *st.session_state.chat_sessions[active_chat]]
                )
                answer = response.choices[0].message.content
                st.session_state.chat_sessions[active_chat].append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")
    st.rerun()