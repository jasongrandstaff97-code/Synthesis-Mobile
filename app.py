from flask import Flask, render_template, request, jsonify
import synthesis_engine
import os

app = Flask(__name__)

# --- REAL SEARCH PLACEHOLDER ---
def perform_real_google_search(query):
    return [
        {"title": "System Status", "snippet": "Search connected successfully.", "source": "SynthesisAI"}
    ]

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_query', methods=['POST'])
def process_query():
    data = request.json
    user_query = data.get('query')
    if not user_query: return jsonify({"error": "No query"}), 400

    # Execute the Brain
    search_results = perform_real_google_search(user_query)
    synthesis_result = synthesis_engine.run_synthesis_cycle(user_query, search_results)
    
    return jsonify(synthesis_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)