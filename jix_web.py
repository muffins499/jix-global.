import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime

# --- 1. MEMORY ENGINE ---
CHATS_FILE = "jix_brain_v12.json"
SETTINGS_FILE = "jix_settings.json"

def load_data(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r") as f: return json.load(f)
    except: pass
    return default

if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_data(CHATS_FILE, {})
if "active_title" not in st.session_state:
    st.session_state.active_title = "New Chat"
if "user_prefs" not in st.session_state:
    st.session_state.user_prefs = load_data(SETTINGS_FILE, {"user_name": "Pathe", "personality": "Strategic Advisor"})

# --- 2. THE "PREMIUM" UI ---
st.set_page_config(page_title="JIX OS", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    [data-testid="stChatMessage"] { background-color: #1c2128 !important; border-radius: 12px; border: 1px solid #30363d; max-width: 850px; margin: 0 auto 10px auto; }
    .stChatInputContainer { max-width: 850px; margin: 0 auto; }
    .stButton button { border-radius: 8px; transition: 0.3s; }
    .stButton button:hover { border-color: #1f6feb; color: #1f6feb; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR COMMANDS ---
with st.sidebar:
    st.title("🌐 JIX OS")
    st.caption(f"System Time: {datetime.now().strftime('%H:%M')} | User: {st.session_state.user_prefs['user_name']}")
    
    if st.button("➕ Initialize New Session", use_container_width=True):
        st.session_state.active_title = "New Chat"
        st.rerun()
    
    st.divider()
    st.subheader("Neural History")
    for title in list(st.session_state.all_chats.keys())[::-1]:
        if st.button(f"📄 {title[:22]}", key=title, use_container_width=True):
            st.session_state.active_title = title
            st.rerun()
    
    st.divider()
    with st.expander("🛠️ OS Settings"):
        st.session_state.user_prefs["user_name"] = st.text_input("Engineer Name", st.session_state.user_prefs["user_name"])
        if st.button("Save & Reboot"):
            with open(SETTINGS_FILE, "w") as f: json.dump(st.session_state.user_prefs, f)
            st.rerun()
    
    if st.button("🗑️ Wipe All Data", type="secondary"):
        st.session_state.all_chats = {}
        if os.path.exists(CHATS_FILE): os.remove(CHATS_FILE)
        st.rerun()

# --- 4. ENGINE CONNECT ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

# --- 5. INTERFACE & QUICK TOOLS ---
active_id = st.session_state.active_title
if active_id not in st.session_state.all_chats:
    st.session_state.all_chats[active_id] = []

# Dynamic Welcome Message
if not st.session_state.all_chats[active_id]:
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    st.markdown(f"<h1 style='text-align: center; margin-top: 100px; font-weight: 300;'>{greeting}, Engineer {st.session_state.user_prefs['user_name']}.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Neural Link Standby. Select a core objective below.</p>", unsafe_allow_html=True)

# Display Messages
for msg in st.session_state.all_chats[active_id]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. THE "STRATEGIC TOOLBOX" ---
st.write("")
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,2])
with col1: s_biz = st.button("🚀 Scale")
with col2: s_code = st.button("📝 Code")
with col3: s_trend = st.button("📊 Trends")
with col4: s_plan = st.button("📅 Plan")

user_input = st.chat_input("Input Command to JIX...")

# Surprise: Logic for "Plan" and deeper prompts
final_prompt = user_input
if s_biz: final_prompt = "Analyze market vectors and provide a 3-stage scaling strategy for a tech startup."
if s_code: final_prompt = "Draft a clean, modular Python script for a data processing automation tool."
if s_trend: final_prompt = "Identify the top 3 disruptive technologies emerging in mid-2026."
if s_plan: final_prompt = "Create a high-level project roadmap for the next 90 days of JIX development."

# --- 7. THE BRAIN ---
if final_prompt:
    if active_id == "New Chat":
        active_id = " ".join(final_prompt.split()[:3]) + "..."
        st.session_state.all_chats[active_id] = []
        st.session_state.active_title = active_id

    st.session_state.all_chats[active_id].append({"role": "user", "content": final_prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("JIX IS PROCESSING..."):
            sys_msg = (
                f"You are JIX GLOBAL OS. Lead Engineer: {st.session_state.user_prefs['user_name']}. "
                "Current Date: March 2026. Tone: High-level Strategic Advisor. "
                "Structure: 1. Executive Summary, 2. Core Analysis, 3. Strategic Objectives."
            )
            hist = [{"role": "system", "content": sys_msg}] + st.session_state.all_chats[active_id][-10:]
            
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist)
            reply = res.choices[0].message.content
            st.markdown(reply)
            st.session_state.all_chats[active_id].append({"role": "assistant", "content": reply})
            
            with open(CHATS_FILE, "w") as f: json.dump(st.session_state.all_chats, f)
    st.rerun()
