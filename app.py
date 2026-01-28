import os
import io
from dotenv import load_dotenv
import streamlit as st
from google import genai
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# 1. SETUP
load_dotenv()
st.set_page_config(page_title="Synthesis Engine", page_icon="🧠")

# 2. INTERNAL SECURITY GATE
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("Access Key", type="password")
    if st.button("Unlock"):
        if pwd == os.getenv("APP_PASSWORD"):
            st.session_state.auth = True
            st.rerun()
        else: st.error("Denied")
    st.stop()

# 3. INITIALIZE CLIENTS (The New google-genai way)
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("🧠 Synthesis Engine v3.0")
st.caption("Main Brain: Groq | Agents: Gemini 3 Flash")

# 4. INPUT (Voice or Text)
col1, col2 = st.columns([1, 3])
with col1:
    st.write("Voice Input:")
    v_input = speech_to_text(start_prompt="🎤 Start", stop_prompt="🛑 Stop", key='stt')
with col2:
    manual_input = st.text_area("Or type here:", value=v_input if v_input else "")

# 5. EXECUTION
if st.button("EXECUTE COUNCIL"):
    input_text = manual_input if manual_input else v_input
    if not input_text:
        st.warning("Needs input.")
    else:
        with st.status("Council Deliberating...", expanded=True):
            # VISIONARY (Gemini 3 Flash - Shorthand)
            v_res = gemini.models.generate_content(
                model="gemini-3-flash-preview",
                config={'system_instruction': "ROLE:Visionary. TASK:Max-potential. FORMAT:Shorthand."},
                contents=input_text
            )
            
            # SKEPTIC (Gemini 3 Flash - Shorthand)
            s_res = gemini.models.generate_content(
                model="gemini-3-flash-preview",
                config={'system_instruction': "ROLE:Skeptic. TASK:Critical-risks. FORMAT:Shorthand."},
                contents=input_text
            )

            # JUDGE (Groq - Synthesis)
            verdict = groq.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": f"Synthesize these:\nV: {v_res.text}\nS: {s_res.text}"}]
            )
            st.session_state.verdict = verdict.choices[0].message.content

# 6. OUTPUT & READ ALOUD
if "verdict" in st.session_state:
    st.markdown("---")
    st.subheader("⚖️ Final Verdict")
    st.write(st.session_state.verdict)
    
    if st.button("🔊 Read Verdict Aloud"):
        tts = gTTS(text=st.session_state.verdict, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
