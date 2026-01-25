def generate_ai_response(prompt, system_instruction, model_type="gemini"):
    try:
        if model_type == "gemini":
            genai.configure(api_key=GOOGLE_API_KEY)
            # Switch back to the standard stable name
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", 
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