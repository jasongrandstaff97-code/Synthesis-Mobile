import streamlit as st
import time, concurrent.futures, io, base64
from google import genai 
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder 

# --- SYSTEM CHECK ---
print("--- LOADING NEW VERSION: LLAMA 3.3 ACTIVE ---")

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Synthesis Mobile", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .stTextInput > div > div > input { background-color: #161b22; color: white; border: 1px solid #30363d; border-radius: 8px; }
    .stExpander { border: 1px solid #30363d !important; background-color: #161b22 !important; border-radius: 8px; margin-bottom: 10px; }
    label { display: none !important; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #238636; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ACCESS CONTROL ---
if "auth" not in st.session_state:
    st.title("✦ Portal")
    entered_pw = st.text_input("Key", type="password", placeholder="Access Key")
    if entered_pw == st.secrets.get("APP_PASSWORD", "Synthesis2026"):
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- 3. THE "UNBREAKABLE" ENGINES ---
def run_groq(q, role_prompt, model="llama-3.3-70b-versatile"):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"{role_prompt}: {q}"}], 
            model=model
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Groq Error: {e}"

def run_smart_engine(prompt, role_name):
    try:
        c = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        return c.models.generate_content(model="gemini-2.5-flash", contents=prompt).text
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
            st.warning(f"⚠️ Gemini Quota Hit. {role_name} is failing over to Llama 3.3...")
            return run_groq(prompt, f"Act as the {role_name}", model="llama-3.3-70b-versatile")
        return f"Critical System Error: {e}"

# --- 4. INTERFACE & INPUT ---
st.title("✦ The Council")
query = None

col_text, col_mic = st.columns([0.85, 0.15])
with col_text:
    manual_input = st.text_input("Input", placeholder="Tap mic or type target...")
with col_mic:
    audio_data = mic_recorder(start_prompt="🎤", stop_prompt="⏹", key='recorder')

if audio_data:
    with st.spinner("Transcribing voice..."):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            transcription = client.audio.transcriptions.create(
                file=("speech.wav", audio_data['bytes']),
                model="whisper-large-v3", 
                response_format="text"
            )
            query = transcription
        except Exception as e:
            st.error(f"Mic Error: {e}")
elif manual_input:
    query = manual_input

# --- 5. THE DELIBERATION LOOP ---
if query:
    st.markdown("---")
    with st.spinner("The Council is deliberating..."):
        with concurrent.futures.ThreadPoolExecutor() as ex:
            v_future = ex.submit(run_groq, query, "Act as The Visionary & Librarian. Start with a relevant quote from a classic book or philosopher, then expand optimistically.")
            s_future = ex.submit(run_groq, query, "Act as The Skeptic. Brutally identify logical flaws, risks, and downsides.")
            v_out = v_future.result()
            s_out = s_future.result()

        a_out = run_smart_engine(f"Architect: Create a concrete implementation plan for '{query}' that solves these problems: {s_out}", "Architect")
        time.sleep(2.0) 
        j_out = run_smart_engine(f"Judge: Weighing the Visionary ({v_out}) and Skeptic ({s_out}), deliver a final verdict and conclusion on '{query}'.", "Judge")

    with st.expander("🔥 Visionary & Library Quote"):
        st.markdown(v_out)
    with st.expander("🛡️ Skeptic's Critique"):
        st.markdown(s_out)
    with st.expander("📐 Architect's Blueprint"):
        st.markdown(a_out)
    
    st.success("⚖️ The Final Verdict")
    st.write(j_out)

    if st.button("🔊 Read Verdict Out Loud"):
        try:
            with st.spinner("Synthesizing audio..."):
                tts = gTTS(text=j_out, lang='en')
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                b64 = base64.b64encode(audio_buffer.read()).decode()
                st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Audio Error: {e}")

    if st.button("🗑️ Clear Session"):
        st.rerun()