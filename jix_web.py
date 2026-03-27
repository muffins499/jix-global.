import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS  # New Library
from datetime import datetime

# --- 1. SYSTEM CONFIG ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Add it to Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="JIX GLOBAL OS", page_icon="📐", layout="wide")


# --- 2. THE SEARCH TOOL ---
def search_the_web(query):
    """Fetches real-time data from the internet."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if results:
                context = "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])
                return context
    except Exception as e:
        return f"Search failed: {e}"
    return "No live data found."


# --- 3. STATE MANAGEMENT ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Main Link": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Main Link"
if "language" not in st.session_state:
    st.session_state.language = "English"

# --- 4. THE INITIALIZATION ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>📐 JIX GLOBAL</h1>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        user_id = st.text_input("Operator ID (Email)")
        if st.button("INITIALIZE SYSTEM"):
            if "@" in user_id:
                st.session_state.authenticated = True
                st.session_state.user_name = user_id.split('@')[0].capitalize()
                st.rerun()
            else:
                st.warning("Enter a valid Operator ID.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("📐 JIX OS")
    st.caption(f"Operator: {st.session_state.user_name}")
    st.divider()
    st.session_state.language = st.selectbox("Language",
                                             ["English", "Spanish", "French", "German", "Arabic", "Chinese"])

    st.divider()
    if st.button("+ New Channel", use_container_width=True):
        new_name = f"Channel {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()

    for title in st.session_state.chat_sessions.keys():
        if st.button(f"💬 {title}", key=f"nav_{title}", use_container_width=True):
            st.session_state.current_chat = title
            st.rerun()

# --- 6. CHAT LOGIC ---
chat_name = st.session_state.current_chat
st.title(f"📡 {chat_name}")

for msg in st.session_state.chat_sessions[chat_name]:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "📐"):
        st.markdown(msg["content"])

prompt = st.chat_input(f"Ask JIX anything...")

if prompt:
    st.session_state.chat_sessions[chat_name].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="📐"):
        # STEP 1: Check if we need the web
        search_keywords = ["news", "price", "weather", "today", "latest", "who is", "what happened"]
        web_context = ""

        if any(word in prompt.lower() for word in search_keywords):
            with st.status("🌐 Accessing Global Web..."):
                web_context = search_the_web(prompt)
                st.write("Live data retrieved.")

        # STEP 2: Generate Answer
        try:
            sys_instructions = (
                f"You are JIX GLOBAL AI. Creator: Pathe. User: {st.session_state.user_name}. "
                f"Language: {st.session_state.language}. "
                f"Web Context: {web_context if web_context else 'No live data needed.'} "
                "Use the Web Context if it provides real-time information. "
                "Always end with 3 Global Strategy ideas for Pathe."
            )

            history = [{"role": "system", "content": sys_instructions}]
            history.extend(st.session_state.chat_sessions[chat_name][-5:])  # Send last 5 msgs for memory

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history
            )

            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_sessions[chat_name].append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"Sync Error: {e}")
    st.rerun()