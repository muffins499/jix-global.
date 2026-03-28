import streamlit as st
from groq import Groq
import json
import os

# --- 1. CORE CONFIG ---
ENGINEER = "Pathe"
OS_NAME = "JIX"

# --- 2. API CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 Connection Refused: Add GROQ_API_KEY to Secrets.")
    st.stop()

# --- 3. UI STYLING (The Gemini Pro Look) ---
st.set_page_config(page_title=OS_NAME, page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e0e0e0; }
    [data-testid="stChatMessage"] { max-width: 850px; margin: 0 auto; border: none !important; }
    .stChatInputContainer { max-width: 850px; margin: 0 auto; border-radius: 30px !important; }
    h1 { text-align: center; color: #1f1f1f; font-family: sans-serif; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)


# --- 4. RELIABLE MEMORY ---
def load_data():
    if os.path.exists("jix_v3.json"):
        with open("jix_v3.json", "r") as f: return json.load(f)
    return {}


if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_data()

if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title(f"🌐 {OS_NAME}")
    if st.button("➕ New chat", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()

    st.divider()
    st.subheader("Recent")
    for title in reversed(list(st.session_state.all_chats.keys())):
        if st.button(f"💬 {title}", key=title, use_container_width=True):
            st.session_state.active_title = title
            st.rerun()

# --- 6. CHAT INTERFACE ---
active_title = st.session_state.active_title

if active_title in st.session_state.all_chats:
    st.title(active_title)
    for msg in st.session_state.all_chats[active_title]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
else:
    st.title("Where should we start?")

# --- 7. THE BRAIN (Intelligence & Strategy Engine) ---
if prompt := st.chat_input("Enter Global Command..."):
    target_title = active_title

    if active_title == "New Chat":
        # Create a professional title from the prompt
        target_title = " ".join(prompt.split()[:4])
        st.session_state.all_chats[target_title] = []
        st.session_state.active_title = target_title

    # 1. Save User Input
    st.session_state.all_chats[target_title].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Intelligent Response
    with st.chat_message("assistant"):
        with st.spinner("SYST: ANALYZING GLOBAL VECTORS..."):
            try:
                # --- THIS IS THE INTELLIGENCE INJECTION ---
                sys_msg = (
                    f"You are JIX GLOBAL OS. Your Lead Engineer is {ENGINEER}. "
                    "You are a hyper-intelligent strategic advisor. Your tone is professional, "
                    "authoritative, and slightly futuristic. "
                    "RULES: "
                    "1. Never give generic answers. Always look for a 'Global Edge'. "
                    "2. If the user asks a question, answer it, then suggest a way to scale that idea. "
                    "3. ALWAYS end every response with a section titled '--- STRATEGIC OBJECTIVES ---' "
                    "listing 3 actionable, high-level steps Pathe should take next."
                )

                history = [{"role": "system", "content": sys_msg}] + st.session_state.all_chats[target_title][-10:]

                # Using the Llama 3.3 70B model for high-level reasoning
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history,
                    temperature=0.8  # Higher temp = more creative/interesting ideas
                )

                reply = response.choices[0].message.content
                st.markdown(reply)

                # 3. Save & Persist
                st.session_state.all_chats[target_title].append({"role": "assistant", "content": reply})
                with open("jix_brain_v4.json", "w") as f:
                    json.dump(st.session_state.all_chats, f)

            except Exception as e:
                st.error(f"NEURAL ERROR: {e}")

    st.rerun()
