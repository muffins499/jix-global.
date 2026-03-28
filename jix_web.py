import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime, timedelta
from uuid import uuid4

# =====================================================
# 1. CORE DATA
# =====================================================

CHATS_FILE = "jix_v2_history.json"
SETTINGS_FILE = "jix_v2_settings.json"


def load_json(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json_atomic(file, data):
    tmp = file + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, file)


# =====================================================
# 2. SESSION INIT
# =====================================================

if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_json(CHATS_FILE, {})

if "active_id" not in st.session_state:
    st.session_state.active_id = None

if "user_prefs" not in st.session_state:
    saved = load_json(SETTINGS_FILE, {})
    st.session_state.user_prefs = {
        "name": "Pathe",
        "country": "South Africa",
        "model": "llama-3.3-70b-versatile",
        "memory": 6,
        "personality": "You are JIX, a smart strategic AI assistant.",
        **saved,
    }

# =====================================================
# 3. TIME ENGINE
# =====================================================

TZ_MAP = {
    "South Africa": 2,
    "UK": 0,
    "USA (EST)": -5,
    "UAE": 4,
    "India": 5.5,
    "Nigeria": 1,
}

offset = TZ_MAP.get(st.session_state.user_prefs["country"], 2)
local_time = (datetime.utcnow() + timedelta(hours=offset)).strftime("%H:%M")

# =====================================================
# 4. PAGE DESIGN
# =====================================================

st.set_page_config(page_title="JIX GLOBAL", layout="wide")

st.markdown("""
<style>
.stApp {background:#f8f9fa;}
[data-testid="stSidebar"] {
    background:white;
    border-right:1px solid #dadce0;
}
[data-testid="stChatMessage"]{
    background:white;
    border-radius:12px;
    border:1px solid #e0e0e0;
    max-width:800px;
    margin:auto;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 5. SIDEBAR
# =====================================================

with st.sidebar:
    st.title("🌐 JIX OS")
    st.caption(f"📍 {st.session_state.user_prefs['country']} | 🕒 {local_time}")

    if st.button("➕ New Chat", use_container_width=True):
        cid = str(uuid4())
        st.session_state.all_chats[cid] = {
            "title": "New Chat",
            "messages": [],
            "created": datetime.utcnow().isoformat(),
        }
        st.session_state.active_id = cid
        save_json_atomic(CHATS_FILE, st.session_state.all_chats)
        st.rerun()

    st.divider()

    search = st.text_input("🔎 Search chats")

    for cid, chat in reversed(list(st.session_state.all_chats.items())):
        if search.lower() not in chat["title"].lower():
            continue
        if st.button(f"💬 {chat['title'][:22]}", key=cid, use_container_width=True):
            st.session_state.active_id = cid
            st.rerun()

    st.divider()

    # SETTINGS
    with st.expander("⚙️ Settings", expanded=False):

        prefs = st.session_state.user_prefs

        prefs["name"] = st.text_input("Name", prefs["name"])
        prefs["country"] = st.selectbox(
            "Location", list(TZ_MAP.keys()),
            index=list(TZ_MAP.keys()).index(prefs["country"])
        )

        prefs["model"] = st.selectbox(
            "Model",
            ["llama-3.3-70b-versatile", "mixtral-8x7b"],
        )

        prefs["memory"] = st.slider("Conversation Memory", 2, 15, prefs["memory"])

        prefs["personality"] = st.text_area(
            "System Personality",
            prefs["personality"],
            height=120,
        )

        if st.button("Save Settings"):
            save_json_atomic(SETTINGS_FILE, prefs)
            st.success("Saved")

# =====================================================
# 6. CHAT ENGINE
# =====================================================

if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY to secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

active_id = st.session_state.active_id

if not active_id:
    st.markdown(
        f"<h1 style='text-align:center;margin-top:120px;'>"
        f"How can I help you, {st.session_state.user_prefs['name']}?"
        f"</h1>",
        unsafe_allow_html=True,
    )
    st.stop()

chat = st.session_state.all_chats[active_id]

# =====================================================
# 7. CHAT DISPLAY
# =====================================================

for msg in chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================================================
# 8. TOOLBAR
# =====================================================

c1, c2, c3, c4 = st.columns([1, 1, 1, 6])

with c1:
    scale = st.button("🚀 Scale")

with c2:
    code = st.button("📝 Code")

with c3:
    trends = st.button("📊 Trends")

with c4:
    if st.button("🗑 Delete Chat"):
        del st.session_state.all_chats[active_id]
        save_json_atomic(CHATS_FILE, st.session_state.all_chats)
        st.session_state.active_id = None
        st.rerun()

# =====================================================
# 9. INPUT
# =====================================================

user_input = st.chat_input("Message JIX...")

prompt = user_input
if scale:
    prompt = "Give me a startup scaling strategy."
elif code:
    prompt = "Write a clean Python script."
elif trends:
    prompt = "What are the biggest technology trends in 2026?"

# =====================================================
# 10. AI RESPONSE (STREAMING)
# =====================================================

if prompt:

    chat["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        response_text = ""

        stream = client.chat.completions.create(
            model=st.session_state.user_prefs["model"],
            stream=True,
            messages=[
                {
                    "role": "system",
                    "content": st.session_state.user_prefs["personality"],
                }
            ]
            + chat["messages"][-st.session_state.user_prefs["memory"]:],
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            response_text += delta
            placeholder.markdown(response_text + "▌")

        placeholder.markdown(response_text)

    chat["messages"].append({"role": "assistant", "content": response_text})

    # Auto title generation
    if chat["title"] == "New Chat":
        chat["title"] = " ".join(prompt.split()[:4]) + "..."

    save_json_atomic(CHATS_FILE, st.session_state.all_chats)

    st.rerun()

# =====================================================
# 11. FOOTER STATS
# =====================================================

st.caption(
    f"Messages: {len(chat['messages'])} | "
    f"Model: {st.session_state.user_prefs['model']}"
)
