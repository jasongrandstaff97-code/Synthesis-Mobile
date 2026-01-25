import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai

app = Flask(__name__)
# This secret key is required for the login session to work
app.secret_key = "council_secret_vault"

# --- CONFIGURATION ---
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
PASSWORD = os.environ.get("APP_PASSWORD", "Synthesis2026")

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
    user_prompt = data.get('prompt')

    try:
        # The Council Deliberation
        v_res = model.generate_content(f"Visionary: {user_prompt}")
        s_res = model.generate_content(f"Skeptic: Critique {v_res.text}")
        j_res = model.generate_content(f"Judge: Final verdict for {user_prompt}")
        
        # Your Automated Visual Agent (Nano Banano Pro)
        a_res = model.generate_content(f"Artist: Create a high-detail surrealist visual prompt for 'Nano Banano Pro' based on: {j_res.text}")

        # IMPORTANT: These keys match your index.html EXACTLY to fix 'undefined'
        return jsonify({
            "visionary": v_res.text,
            "skeptic": s_res.text,
            "verdict": j_res.text,
            "artist": a_res.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
