from flask import Flask, request, jsonify
from google import genai
import os

app = Flask(__name__)

# Primary Engine: Gemini 2.5 Flash
client_gemini = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# Fallback Engine: Llama (via Groq or similar provider)
# Assuming you have a GROQ_API_KEY for Llama access
import groq
client_llama = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

def run_judge_logic(prompt):
    try:
        # ATTEMPT 1: Gemini 2.5 Flash
        response = client_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text, "Gemini 2.5 Flash"

    except Exception as e:
        print(f"Gemini failed: {e}. Switching to Llama fallback...")
        
        # ATTEMPT 2: Failover to Llama 3.3 70B
        response = client_llama.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content, "Llama 3.3 70B (Fallback)"

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    user_prompt = f"Act as a Judge and synthesize these results: {data.get('prompt')}"
    
    output, provider = run_judge_logic(user_prompt)
    
    return jsonify({
        "success": True,
        "engine_used": provider,
        "output": output
    })