from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    
    # Check if 'prompt' exists in the incoming JSON
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing prompt in request"}), 400
    
    user_prompt = data['prompt']
    
    # This is where your synthesis logic (Judge) will go
    response_data = {
        "status": "success",
        "input_received": user_prompt,
        "message": f"Synthesis engine processing: {user_prompt}"
    }
    
    return jsonify(response_data)

if __name__ == "__main__":
    # HOST '0.0.0.0' is critical for GitHub Codespaces and Docker
    # PORT 5000 is what your curl command is targeting
    app.run(host='0.0.0.0', port=5000, debug=True)