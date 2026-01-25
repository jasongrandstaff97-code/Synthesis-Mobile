import os
import google.generativeai as genai
from groq import Groq

# API Setup
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def generate_ai_response(prompt, system_instruction, model_type="gemini"):
    try:
        if model_type == "gemini":
            if not GOOGLE_API_KEY:
                return "Error: Missing Google API Key"
            
            genai.configure(api_key=GOOGLE_API_KEY)
            
            # Use the most basic, stable model name
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", 
                system_instruction=system_instruction
            )
            
            response = model.generate_content(prompt)
            return response.text
        
        elif model_type == "groq" and groq_client:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
            
    except Exception as e:
        # LOG THE REAL ERROR IN THE TERMINAL
        print(f"❌ ENGINE CRASH: {str(e)}")
        # Return a string so the app doesn't break
        return f"AI Agent Error: {str(e)}"

def run_synthesis_cycle(query, context_list):
    # Ensure context is a string
    context_str = "\n".join([f"- {item.get('title')}: {item.get('snippet')}" for item in context_list])

    # Agent 1: Visionary
    vis_out = generate_ai_response(f"Q: {query}\nData: {context_str}", "You are a visionary.", "gemini")
    
    # Agent 2: Skeptic
    skep_out = generate_ai_response(f"Plan: {vis_out}", "You are a skeptic.", "groq")
    
    # Agent 3: Judge
    verdict_out = generate_ai_response(f"Q: {query}\nVis: {vis_out}\nSkep: {skep_out}", "You are a judge.", "gemini")

    return {
        "visionary": vis_out,
        "skeptic": skep_out,
        "final_verdict": verdict_out
    }