import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "council_secret_vault"
from synthesis_engine import SynthesisEngine
engine = SynthesisEngine()
# --- CONFIGURATION ---
# We use the 'models/' prefix to solve the 404 error you saw in the terminal
API_KEY = os.environ.get("GOOGLE_API_KEY")
PASSWORD = os.environ.get("APP_PASSWORD", "Synthesis2026")

if API_KEY:
    genai.configure(api_key=API_KEY)

# Using 'gemini-1.5-flash' directly is usually best, 
# but we wrap it in a try-block just in case.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"--- MODEL INIT ERROR: {e} ---")

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        return "Wrong Council Key.", 403
    return render_template('login.html')

@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_prompt = data.get('prompt', '')

    try:
        # Step 1: Visionary
        v_res = model.generate_content(f"Visionary: {user_prompt}")
        
        # Step 2: Skeptic
        s_res = model.generate_content(f"Skeptic: Critique this: {v_res.text}")
        
        # Step 3: Judge
        j_res = model.generate_content(f"Judge: Final verdict for: {user_prompt}")
        
        # Step 4: Artist (Nano Banano Pro)
        a_res = model.generate_content(f"Artist: Visual prompt for 'Nano Banano Pro' based on: {j_res.text}")

        return jsonify({
            "visionary": v_res.text,
            "skeptic": s_res.text,
            "verdict": j_res.text,
            "artist": a_res.text
        })

    except Exception as e:
        # This will tell us if it's still a 404 or a new error (like 429 quota)
        print(f"--- ACTUAL ERROR: {e} ---")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
