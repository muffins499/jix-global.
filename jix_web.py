import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime, timedelta

# --- 1. CORE DATA & SETTINGS ---
CHATS_FILE = "jix_v1_history.json"
SETTINGS_FILE = "jix_v1_settings.json"

def load_json(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"JSON load error ({file}):", e)
    return default

# Atomic save (prevents corruption)
def save_json_atomic(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, path)

# Initialize user profile safely
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_json(CHATS_FILE, {})

if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"

if "user_prefs" not in st.session_state:
    saved = load_json(SETTINGS_FILE, {})
    st.session_state.user_prefs = {"name": "Pathe", "country": "South Africa"}
    st.session_state.user_prefs.update(saved)

# --- 2. TIME ENGINE (CRASH-PROOF) ---
TZ_MAP = {
    "South Africa": 2,
    "UK": 0,
    "USA (EST)": -5,
    "UAE": 4,
    "India": 5.5,
    "Nigeria": 1,
}

user_country = st.session_state.user_prefs.get("country", "South Africa")
offset = TZ_MAP.get(user_country, 2)
local_time = (datetime.utcnow() + timedelta(hours=offset)).strftime("%H:%M")

# --- 3. DESIGN ---
st.set_page_config(page_title="JIX GLOBAL", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8f9fa; color: #202124; }
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #dadce0;
}
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #dadce0;
    border-radius: 12px;
    max-width: 800px;
    margin: 0 auto 10px auto;
}
.stChatInputContainer { max-width: 800px; margin: 0 auto; }
.stButton button { border-radius: 20px; border: 1px solid #dadce0; }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌐 JIX OS")
    st.caption(f"📍 {user_country} | 🕒 {local_time}")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()

    st.divider()

    for title in list(st.session_state.all_chats.keys())[::-1]:
        if st.button(f"💬 {title[:20]}", key=title, use_container_width=True):
            st.session_state.active_title = title
            st.rerun()

    st.divider()

    with st.expander("⚙️ Settings"):
        prefs = st.session_state.user_prefs

        prefs["name"] = st.text_input(
            "Name",
            prefs.get("name", "Pathe")
        )

        countries = list(TZ_MAP.keys())
        current_index = countries.index(
            prefs.get("country", "South Africa")
        )

        prefs["country"] = st.selectbox(
            "Location",
            countries,
            index=current_index
        )

        if st.button("Save Settings"):
            save_json_atomic(SETTINGS_FILE, prefs)
            st.rerun()

# --- 5. CHAT INTERFACE ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

active_id = st.session_state.active_title

if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

# Welcome message
if not st.session_state.all_chats[active_id]:
    st.markdown(
        f"<h1 style='text-align:center;margin-top:100px;font-weight:400;'>"
        f"How can I help you, {st.session_state.user_prefs.get('name','Pathe')}?"
        f"</h1>",
        unsafe_allow_html=True
    )

# Safe message rendering
for msg in st.session_state.all_chats[active_id]:
    role = msg.get("role", "assistant")
    content = msg.get("content", "")
    with st.chat_message(role):
        st.markdown(content)

# --- 6. TOOLBAR & INPUT ---
st.write("")
c1, c2, c3, _ = st.columns([1,1,1,5])

with c1:
    s_biz = st.button("🚀 Scale")
with c2:
    s_code = st.button("📝 Code")
with c3:
    s_trend = st.button("📊 Trends")

user_input = st.chat_input("Message JIX...")

prompt = user_input
if s_biz:
    prompt = "Give me a scaling strategy."
if s_code:
    prompt = "Write a Python script."
if s_trend:
    prompt = "What are 2026 tech trends?"

# --- 7. AI RESPONSE ---
if prompt:

    # Prevent chat title collisions
    if active_id == "New Chat":
        base = " ".join(prompt.split()[:3]) + "..."
        new_id = base
        i = 1
        while new_id in st.session_state.all_chats:
            new_id = f"{base} ({i})"
            i += 1

        st.session_state.all_chats[new_id] = []
        st.session_state.active_title = new_id
        active_id = new_id

    st.session_state.all_chats[active_id].append(
        {"role": "user", "content": prompt}
    )

    history = st.session_state.all_chats[active_id][-5:]

    with st.chat_message("assistant"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are JIX, helping {st.session_state.user_prefs.get('name','Pathe')}."
                }
            ] + history
        )

        reply = res.choices[0].message.content
        st.markdown(reply)

        st.session_state.all_chats[active_id].append(
            {"role": "assistant", "content": reply}
        )

        save_json_atomic(CHATS_FILE, st.session_state.all_chats)
