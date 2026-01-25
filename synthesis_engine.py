import os
import google.generativeai as genai

class SynthesisEngine:
    def __init__(self):
        # Initialize the API using the environment variable
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("--- ENGINE ERROR: GOOGLE_API_KEY NOT FOUND ---")
            return
        
        genai.configure(api_key=api_key)
        # Using 1.5-flash for speed and reliability
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def deliberate(self, user_prompt):
        try:
            # Agent 1: The Visionary (Creative/Optimistic)
            v_res = self.model.generate_content(f"Visionary Agent: Provide an optimistic, high-level perspective on: {user_prompt}")
            v_text = v_res.text

            # Agent 2: The Skeptic (Critical/Analytical)
            s_res = self.model.generate_content(f"Skeptic Agent: Critique this vision: {v_text}")
            s_text = s_res.text

            # Agent 3: The Judge (Balanced/Final)
            j_res = self.model.generate_content(f"Judge Agent: Provide a final balanced verdict for: {user_prompt}")
            j_text = j_res.text

            # Agent 4: Nano Banano Pro Artist (Visual Synthesis)
            a_res = self.model.generate_content(f"Artist: Create a detailed, surreal visual prompt for 'Nano Banano Pro' based on: {j_text}")
            a_text = a_res.text

            return {
                "visionary": v_text,
                "skeptic": s_text,
                "verdict": j_text,
                "artist": a_text
            }

        except Exception as e:
            print(f"--- ENGINE ERROR: {e} ---")
            return {"error": str(e)}

# Allows you to test the engine directly from the terminal
if __name__ == "__main__":
    engine = SynthesisEngine()
    test_result = engine.deliberate("The future of human-AI synthesis.")
    print(test_result)
