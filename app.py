import os
import io
import time
from dotenv import load_dotenv
import streamlit as st
from google import genai
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# --- SYSTEM CONFIG & IOS STYLING ---
load_dotenv()
st.set_page_config(page_title="Synthesis Engine", page_icon="🧠", layout="centered")

# Custom CSS for iOS Glassmorphism & Accordion Folders
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1c1c1e 0%, #000000 100%);
        font-family: 'Inter', -apple-system, sans-serif;
        color: #FFFFFF;
    }
    
    /* Glassmorphism Cards */
    .stAlert, .stExpander, div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        margin-bottom: 15px;
    }
    
    /* Buttons - iOS Blue & Rounded */
    div.stButton > button {
        border-radius: 25px;
        background-color: #0A84FF;
        color: white;
        border: none;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.2s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #409CFF;
        transform: scale(1.02);
    }
    
    /* Input Areas */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        border: none !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SECURITY GATE ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; margin-top: 20%;'>🔒</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Access Key", type="password", placeholder="Verification Required")
        if st.button("Unlock Engine"):
            if pwd == os.getenv("APP_PASSWORD"):
                st.session_state.auth = True
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

# --- INITIALIZE CLIENTS ---
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- MAIN UI ---
st.title("Synthesis Engine")
st.caption("Designed in California | Powered by Gemini 3 Flash & Groq")

# Interaction Container
with st.container():
    # Mic Input Integration
    v_input = speech_to_text(start_prompt="🎤 Tap to Speak", stop_prompt="🛑 Finish", key='stt')
    manual_input = st.text_area("Input clinical data or concept:", value=v_input if v_input else "", height=150)
    
    if st.button("Execute Synthesis"):
        input_text = manual_input if manual_input else v_input
        if not input_text:
            st.warning("Input required to begin.")
        else:
            with st.status("Engine Warming...", expanded=False) as status:
                # TOKEN COMPRESSION: Visionary
                v_res = gemini.models.generate_content(
                    model="gemini-3-flash-preview",
                    config={'system_instruction': "ROLE:Visionary. TASK:Max-potential. MODE:Shorthand. No-Prose."},
                    contents=input_text
                )
                
                # TOKEN COMPRESSION: Skeptic
                s_res = gemini.models.generate_content(
                    model="gemini-3-flash-preview",
                    config={'system_instruction': "ROLE:Skeptic. TASK:Clinical-Risk. MODE:Shorthand. No-Prose."},
                    contents=input_text
                )

                # JUDGE (Llama 3.3 70B Versatile)
                verdict = groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Synthesize debate into clinical verdict:\nV: {v_res.text}\nS: {s_res.text}"}]
                )
                st.session_state.v_out = v_res.text
                st.session_state.s_out = s_res.text
                st.session_state.verdict = verdict.choices[0].message.content
                status.update(label="Synthesis Finalized", state="complete")

# --- OUTPUT: ACCORDION FOLDERS ---
if "verdict" in st.session_state:
    st.markdown("---")
    
    # The Judge's Verdict (Top Level)
    st.markdown("### ⚖️ Final Verdict")
    st.info(st.session_state.verdict)
    
    if st.button("🔊 Read Verdict Aloud"):
        tts = gTTS(text=st.session_state.verdict, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)

    # Agents (Collapsed Accordions)
    with st.expander("📂 Visionary Perspective"):
        st.write(st.session_state.v_out)
        
    with st.expander("📂 Skeptic Perspective"):
        st.write(st.session_state.s_out)
