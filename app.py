import os
import requests
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
from groq import Groq

app = Flask(__name__)

# --- 1. CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- 2. TOOLS (OPEN LIBRARY) ---
def search_books(query):
    try:
        url = f"https://openlibrary.org/search.json?q={query}&fields=title,author_name&limit=3"
        response = requests.get(url, timeout=5)
        docs = response.json().get('docs', [])
        return [{"title": d.get('title'), "author": d.get('author_name', ['Unknown'])[0]} for d in docs]
    except:
        return []

# --- 3. THE COUNCIL (THE BRAIN) ---
def get_council_response(query, book_context):
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini = genai.GenerativeModel("gemini-1.5-flash")
        groq = Groq(api_key=GROQ_API_KEY)

        context_text = "\n".join([f"- {b['title']} by {b['author']}" for b in book_context])

        # A. THE VISIONARY (Gemini)
        visionary_out = gemini.generate_content(f"Topic: {query}\nBooks: {context_text}\nPlan an optimistic path.").text

        # B. THE SKEPTIC (Groq)
        skep_res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a brutal skeptic."}, {"role": "user", "content": visionary_out}]
        )
        skeptic_out = skep_res.choices[0].message.content

        # C. THE JUDGE (Gemini)
        verdict_out = gemini.generate_content(f"Verdict for {query}. Vision: {visionary_out}. Skeptic: {skeptic_out}.").text

        # D. THE ARTIST (Nano Banano Pro Prompt Generator)
        artist_prompt = f"Create a cinematic, 8k, hyper-detailed image prompt for 'Nano Banano Pro' based on: {verdict_out}."
        image_prompt = gemini.generate_content(artist_prompt).text

        return {"visionary": visionary_out, "skeptic": skeptic_out, "verdict": verdict_out, "nano_banano": image_prompt}
    except Exception as e:
        return {"error": str(e)}

# --- 4. THE UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #050505; color: #0f0; font-family: monospace; padding: 20px; padding-bottom: 80px; }
        .card { background: #111; border: 1px solid #333; margin-bottom: 10px; border-radius: 8px; }
        .card-header { padding: 15px; cursor: pointer; background: #1a1a1a; font-weight: bold; }
        .card-body { padding: 15px; color: #ccc; display: none; line-height: 1.6; }
        .open .card-body { display: block; }
        .input-zone { position: fixed; bottom: 0; left: 0; width: 100%; background: #000; padding: 15px; display: flex; box-sizing: border-box; }
        input { flex: 1; padding: 12px; background: #222; border: 1px solid #444; color: #fff; }
        button { padding: 12px 20px; background: #0f0; border: none; font-weight: bold; margin-left: 10px; }
        #loader { text-align: center; color: yellow; display: none; margin-bottom: 20px; }
        .nano-card { border: 1px solid yellow; color: yellow; }
    </style>
</head>
<body>
    <h1>SYNTHESIS AI</h1>
    <div id="loader">CONSULTING THE COUNCIL...</div>
    <div id="results"></div>
    <div class="input-zone">
        <input type="text" id="query" placeholder="Type command...">
        <button onclick="run()">GO</button>
    </div>
    <script>
        function toggle(el) { el.parentElement.classList.toggle('open'); }
        async function run() {
            const q = document.getElementById('query').value;
            if(!q) return;
            document.getElementById('loader').style.display = 'block';
            const res = await fetch('/process', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: q})
            });
            const data = await res.json();
            document.getElementById('loader').style.display = 'none';
            document.getElementById('results').innerHTML = `
                <div class="card"><div class="card-header" onclick="toggle(this)">🔥 VISIONARY</div><div class="card-body">${data.visionary}</div></div>
                <div class="card"><div class="card-header" onclick="toggle(this)">🛡️ SKEPTIC</div><div class="card-body">${data.skeptic}</div></div>
                <div class="card open"><div class="card-header" onclick="toggle(this)">⚖️ VERDICT</div><div class="card-body">${data.verdict}</div></div>
                <div class="card nano-card open"><div class="card-header" onclick="toggle(this)">🎨 NANO BANANO PROMPT</div><div class="card-body">${data.nano_banano}</div></div>
            `;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process():
    query = request.json.get('query')
    books = search_books(query)
    return jsonify(get_council_response(query, books))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)