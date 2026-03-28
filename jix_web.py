import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime, timedelta

# --- 1. CORE DATA ---
CHATS_FILE = "jix_brain_v13.json"
SETTINGS_FILE = "jix_settings.json"

def load_data(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r") as f: return json.load(f)
    except: pass
    return default

# Initialize states
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_data(CHATS_FILE, {})
if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"
if "user_prefs" not in st.session_state:
    st.session_state.user_prefs = load_data(SETTINGS_FILE, {
        "user_name": "Pathe", 
        "country": "South Africa",
        "timezone_offset": 2 
    })

# --- 2. TIME CALCULATOR ---
# Simplified timezone offsets for major regions
TZ_MAP = {
    "South Africa": 2, "UK": 0, "USA (EST)": -5, "USA (PST)": -8, 
    "UAE": 4, "India": 5.5, "Australia (AEST)": 10, "Nigeria": 1
}

current_offset = TZ_MAP.get(st.session_state.user_prefs["country"], 0)
# Calculate local time based on UTC
local_now = datetime.utcnow() + timedelta(hours=current_offset)
current_hour = local_now.hour
time_str = local_now.strftime("%H:%M")

# --- 3. SLEEKER (LIGHTER) DARK THEME ---
st.set_page_config(page_title="JIX OS", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    /* Lighter charcoal for better visibility */
    .stApp { background-color: #202124; color: #e8eaed; }
    [data-testid="stSidebar"] { background-color: #2d2e30 !important; border-right: 1px solid #3c4043; }
    [data-testid="stChatMessage"] { background-color: #303134 !important; border-radius: 12px; max-width: 850px; margin: 0 auto 10px auto; }
    .stChatInputContainer { max-width: 850px; margin: 0 auto; }
    h1, p { font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & SETTINGS ---
with st.sidebar:
    st.title("🌐 JIX OS")
    st.caption(f"📍 {st.session_state.user_prefs['country']} | 🕒 {time_str}")
    
    if st.button("➕ Initialize New Session", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()
    
    st.divider()
    # Chat History
    for title in list(st.session_state.all_chats.keys())[::-1]:
        if st.button(f"📄 {title[:20]}", key=title, use_container_width=True):
            st.session_state.active_title = title
            st.rerun()
    
    st.divider()
    with st.expander("🛠️ OS Config"):
        st.session_state.user_prefs["user_name"] = st.text_input("Engineer Name", st.session_state.user_prefs["user_name"])
        st.session_state.user_prefs["country"] = st.selectbox("Current Location", list(TZ_MAP.keys()))
        if st.button("💾 Sync OS Settings", use_container_width=True):
            with open(SETTINGS_FILE, "w") as f: json.dump(st.session_state.user_prefs, f)
            st.rerun()

    if st.button("🗑️ Wipe All History", type="secondary"):
        st.session_state.all_chats = {}
        if os.path.exists(CHATS_FILE): os.remove(CHATS_FILE)
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.stop()

active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

# Dynamic Greeting
if not st.session_state.all_chats[active_id]:
    greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
    st.markdown(f"<h1 style='text-align: center; margin-top: 100px;'>{greeting}, Engineer {st.session_state.user_prefs['user_name']}.</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #9aa0a6;'>Neural Link established in {st.session_state.user_prefs['country']}.</p>", unsafe_allow_html=True)

for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. TOOLBAR & INPUT ---
st.write("")
c1, c2, c3, c4 = st.columns([1,1,1,5])
with c1: s_biz = st.button("🚀 Scale")
with c2: s_code = st.button("📝 Code")
with c3: s_trend = st.button("📊 Trends")

user_input = st.chat_input("Command JIX...")
final_prompt = user_input
if s_biz: final_prompt = "Provide a high-level scaling strategy."
if s_code: final_prompt = "Draft a modular Python script."
if s_trend: final_prompt = "What are the top tech trends for 2026?"

if final_prompt:
    if active_id == "New Chat":
        active_id = " ".join(final_prompt.split()[:3]) + "..."
        st.session_state.all_chats[active_id] = []
        st.session_state.active_title = active_id

    st.session_state.all_chats[active_id].append({"role": "user", "content": final_prompt})
    
    with st.chat_message("assistant"):
        sys = f"You are JIX OS for {st.session_state.user_prefs['user_name']}. Location: {st.session_state.user_prefs['country']}."
        hist = [{"role": "system", "content": sys}] + st.session_state.all_chats[active_id][-10:]
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist)
        reply = res.choices[0].message.content
        st.markdown(reply)
        st.session_state.all_chats[active_id].append({"role": "assistant", "content": reply})
        with open(CHATS_FILE, "w") as f: json.dump(st.session_state.all_chats, f)
    st.rerun()
