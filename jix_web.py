import streamlit as st
from groq import Groq
import datetime

# --- 1. SEARCH CHECK ---
try:
    from duckduckgo_search import DDGS

    search_available = True
except ImportError:
    search_available = False

# --- 2. SYSTEM CONFIG ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="JIX GLOBAL OS", page_icon="📐", layout="wide")

# --- 3. PERSISTENT STATE ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Main Link": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Main Link"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Pathe"  # Hardcoded so it NEVER forgets you

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📐 JIX OS")
    st.subheader(f"Engineer: {st.session_state.user_name}")

    if not search_available:
        st.error("⚠️ Search Module Offline. Check requirements.txt")
    else:
        st.success("🌐 Search Module Online")

    if st.button("+ New Channel", use_container_width=True):
        name = f"Channel {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[name] = []
        st.session_state.current_chat = name
        st.rerun()

# --- 5. CHAT LOGIC ---
chat_name = st.session_state.current_chat
st.title(f"📡 {chat_name}")

for msg in st.session_state.chat_sessions[chat_name]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Command JIX...")

if prompt:
    st.session_state.chat_sessions[chat_name].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="📐"):
        web_data = ""
        # Auto-trigger search for news/liverpool/scores
        if search_available and any(x in prompt.lower() for x in ["news", "score", "who", "latest", "liverpool"]):
            with st.spinner("Searching Global Web..."):
                try:
                    with DDGS() as ddgs:
                        results = [r for r in ddgs.text(prompt, max_results=3)]
                        web_data = "\n".join([f"{r['title']}: {r['body']}" for r in results])
                except:
                    web_data = "Search timed out."

        # Brain response
        sys_prompt = (
            f"You are JIX GLOBAL AI. Created by Pathe. "
            f"Current Web Info: {web_data if web_data else 'None'}. "
            "Use web info to answer accurately. Always give 3 Global Ideas at the end."
        )

        history = [{"role": "system", "content": sys_prompt}]
        history.extend(st.session_state.chat_sessions[chat_name][-10:])

        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=history)
        ans = res.choices[0].message.content
        st.markdown(ans)
        st.session_state.chat_sessions[chat_name].append({"role": "assistant", "content": ans})
    st.rerun()
