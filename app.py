import streamlit as st
import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# --- INITIALIZATION & STYLING ---
load_dotenv()
st.set_page_config(page_title="Synthesis Engine", page_icon="🧠", layout="centered")

# iOS-inspired Custom CSS
st.markdown("""
    <style>
    .main { background-color: #F2F2F7; }
    div.stButton > button {
        border-radius: 12px;
        background-color: #007AFF;
        color: white;
        border: none;
        transition: 0.3s;
        font-weight: bold;
    }
    div.stButton > button:hover { background-color: #0051A8; }
    .stTextArea textarea { border-radius: 15px; border: 1px solid #C7C7CC; }
    .verdict-box {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #007AFF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SECURITY GATE ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔐 Synthesis Security</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("Access Key", type="password", placeholder="Enter Password")
            if st.button("Unlock Engine"):
                if pwd == os.getenv("APP_PASSWORD"):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
        return False
    return True

if check_password():
    # --- API CLIENTS ---
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    st.title("🧠 Synthesis Engine")
    st.caption("Main Brain: Groq (Llama 3) | Agents: Gemini 3 Flash")

    # --- INPUT SECTION ---
    user_input = st.text_area("Input Concept:", height=150, placeholder="Describe the clinical or behavioral concept...")
    
    col_mic, col_exec = st.columns([1,1])
    with col_mic:
        if st.button("🎤 Mic / Dictate"):
            st.info("Use system dictation (Win+H / Cmd+Control+S)")
            
    # --- CORE ENGINE LOGIC (TOKEN COMPRESSED) ---
    if col_exec.button("🚀 EXECUTE SYNTHESIS"):
        if not user_input:
            st.error("Input required.")
        else:
            with st.status("Council Processing...", expanded=True) as status:
                
                # AGENT 1: Visionary (Compressed Gemini)
                # Shorthand prompt saves roughly 40-60% tokens per call
                v_model = genai.GenerativeModel('gemini-1.5-flash')
                v_prompt = f"ROLE:Visionary. TASK:Max-potential of {user_input}. FORMAT:Shorthand-Bullets. No intro/outro."
                visionary_res = v_model.generate_content(v_prompt)
                st.write("✅ Visionary mapped.")

                # AGENT 2: Skeptic (Compressed Gemini)
                s_prompt = f"ROLE:Skeptic. TASK:Critical-risks of {user_input}. FORMAT:Shorthand-Bullets. No intro/outro."
                skeptic_res = v_model.generate_content(s_prompt)
                st.write("✅ Skeptic challenged.")

                # AGENT 3: Judge & Main Brain (Groq/Llama 3)
                # Groq synthesizes the shorthand into a professional verdict
                judge_prompt = f"""
                Analyze the following data for a clinical verdict.
                VISIONARY: {visionary_res.text}
                SKEPTIC: {skeptic_res.text}
                
                Instruction: Provide a cohesive synthesis and final path forward.
                """
                
                verdict = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "system", "content": "You are the Senior Clinical Judge. Provide professional, structured verdicts."},
                              {"role": "user", "content": judge_prompt}]
                )
                
                st.session_state.final_verdict = verdict.choices[0].message.content
                status.update(label="Synthesis Complete", state="complete")

    # --- OUTPUT SECTION ---
    if "final_verdict" in st.session_state:
        st.markdown("### ⚖️ Final Verdict")
        st.markdown(f'<div class="verdict-box">{st.session_state.final_verdict}</div>', unsafe_allow_html=True)
        
        # READ VERDICT BUTTON
        if st.button("🔊 Read Verdict Aloud"):
            # Clean text for JS injection
            clean_verdict = st.session_state.final_verdict.replace("'", "\\'").replace("\n", " ")
            js_code = f"""
            <script>
            var msg = new SpeechSynthesisUtterance('{clean_verdict}');
            msg.rate = 0.9; // Slightly slower for clinical clarity
            window.speechSynthesis.speak(msg);
            </script>
            """
            st.components.v1.html(js_code, height=0)

    # --- LOCK BUTTON ---
    if st.sidebar.button("🔒 Secure Lock"):
        st.session_state.authenticated = False
        st.rerun()
