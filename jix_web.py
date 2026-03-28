import streamlit as st
from groq import Groq
import json
import os

# --- 1. BOOT SEQUENCE & IDENTITY ---
ENGINEER = "Pathe"
OS_NAME = "JIX GLOBAL"
OS_VERSION = "2.1-STABLE"

# --- 2. NEURAL COUPLING (API CHECK) ---
if "GROQ_API_KEY" in st.secrets:
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error(f"📡 CONNECTION ERROR: {e}")
        st.stop()
else:
    st.error("🔒 SYSTEM LOCK: GROQ_API_KEY missing in Streamlit Secrets.")
    st.stop()

# --- 3. FUTURISTIC HUD (GLASSMORPHISM UI) ---
# This must be the VERY FIRST streamlit command
st.set_page_config(page_title=OS_NAME, page_icon="📐", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono&display=swap');

    /* Background: Deep Space Gradient */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0a0b10 0%, #000000 100%);
        color: #00f2ff;
        font-family: 'Roboto Mono', monospace;
    }

    /* Sidebar: Frosted Glass Effect */
    section[data-testid="stSidebar"] {
        background: rgba(10, 10, 20, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0, 242, 255, 0.3);
    }

    /* Chat Bubbles: Glowing Glass */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(4px);
    }

    /* User Avatar vs AI Avatar */
    .st-emotion-cache-janm0z { border: 2px solid #00f2ff; }

    /* Input Field: Neon Border */
    .stChatInputContainer {
        border: 1px solid #00f2ff !important;
        background: rgba(0, 0, 0, 0.9) !important;
        border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
    }

    /* Headers: Orbitron Font */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00f2ff !important;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 0 0 15px rgba(0, 242, 255, 0.6);
    }

    /* Hide Streamlit Header/Footer for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. PERSISTENT LOGS (MEMORY) ---
MEMORY_FILE = "jix_memory.json"

def save_mem(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def load_mem():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"MAIN_LINK": []}

if "history" not in st.session_state:
    st.session_state.history = load_mem()

# --- 5. SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.title("📐 JIX_OS")
    st.markdown(f"**STATUS:** `OPERATIONAL`")
    st.markdown(f"**ENGINEER:** `{ENGINEER}`")
    st.markdown(f"**CORE:** `{OS_VERSION}`")
    st.divider()
    
    if st.button("RESET NEURAL LINK", use_container_width=True):
        st.session_state.history = {"MAIN_LINK": []}
        save_mem(st.session_state.history)
        st.rerun()
    
    st.caption("System monitoring active. All inputs are being logged for learning.")

# --- 6. NEURAL INTERFACE (CHAT) ---
st.title("// NEURAL_LINK_ACTIVE")

# Display History
for msg in st.session_state.history["MAIN_LINK"]:
    with st.chat_message(msg["role"], avatar="📐" if msg["role"]=="assistant" else "👤"):
        st.markdown(msg["content"])

# User Command Input
prompt = st.chat_input("Enter Command to JIX...")

if prompt:
    # Append User Input
    st.session_state.history["MAIN_LINK"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant", avatar="📐"):
        with st.spinner("SYST_CALCULATING_STRATEGY..."):
            try:
                # The System Instruction (Brain Setup)
                sys_msg = (
                    f"You are JIX GLOBAL OS. Your lead engineer is {ENGINEER}. "
                    "You are a futuristic, strategic, and highly intelligent AI. "
                    "You remember all past interactions. End every response with a "
                    "'GLOBAL_STRATEGY' section containing 3 high-level ideas."
                )
                
                # Context limit: Send last 10 messages for memory
                messages = [{"role": "system", "content": sys_msg}] + st.session_state.history["MAIN_LINK"][-10:]

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7
                )
                
                full_res = response.choices[0].message.content
                st.markdown(full_res)
                
                # Save to History
                st.session_state.history["MAIN_LINK"].append({"role": "assistant", "content": full_res})
                save_mem(st.session_state.history)
                
            except Exception as e:
                st.error(f"NEURAL_LINK_FAILURE: {e}")
    
    # Force refresh to show new messages
    st.rerun()
