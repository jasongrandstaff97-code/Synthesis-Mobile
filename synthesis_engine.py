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
            genai.configure(api_key=GOOGLE_API_KEY)
            # UPDATED: Using -latest to avoid the 404 error
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest",
                system_instruction=system_instruction
            )
            return model.generate_content(prompt).text
        
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
        print(f"⚠️ Agent Error: {e}")
        return f"Agent Error: {str(e)}"

def run_synthesis_cycle(query, context_list):
    # Format the library and web data for the AI
    context_str = ""
    for item in context_list:
        context_str += f"\n- {item['title']}: {item['snippet']}"

    # 1. Visionary
    vis_sys = "You are THE VISIONARY. Bold, optimistic, and inspired. Cite specific books if they appear in the data."
    visionary_out = generate_ai_response(f"Query: {query}\nData: {context_str}", vis_sys, "gemini")

    # 2. Skeptic
    skep_sys = "You are THE SKEPTIC. Brutal, logical, and cautious. Tear the visionary plan apart."
    skeptic_out = generate_ai_response(f"Plan: {visionary_out}", skep_sys, "groq")

    # 3. Judge
    judge_sys = "You are THE JUDGE. Provide the final synthesized verdict. Use [Source: OpenLibrary] if books were found."
    verdict_out = generate_ai_response(f"Q: {query}\nVis: {visionary_out}\nSkep: {skeptic_out}\nContext: {context_str}", judge_sys, "gemini")

    return {
        "visionary": visionary_out,
        "skeptic": skeptic_out,
        "final_verdict": verdict_out
    }