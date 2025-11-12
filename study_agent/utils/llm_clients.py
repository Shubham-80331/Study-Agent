# utils/llm_clients.py
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv  # <-- 1. IMPORT THE NEW LIBRARY

load_dotenv()  # <-- 2. LOAD THE .env FILE

# --- OPTION 2: Google Gemini (NOW ACTIVE) ---
try:
    # 3. This line now works because load_dotenv() ran first
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Have you created a .env file?")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("LLM Client: Configured Gemini successfully from .env file.")
except Exception as e:
    print(f"LLM Client Error: {e}")
    model = None

# --- Gemini Function for JSON ---
def get_json_response_from_llm(prompt, model=model):
    """
    Sends a prompt to the LLM and attempts to parse a JSON response.
    """
    if not model:
        print("Error: Gemini model is not initialized.")
        return None
        
    try:
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        raw_output = response.text
        return json.loads(raw_output)

    except Exception as e:
        print(f"JSON mode failed, trying text mode fallback: {e}")
        try:
            response = model.generate_content(prompt)
            raw_output = response.text
            json_match = re.search(r'\[.*\]|\{.*\}', raw_output, re.DOTALL)
            
            if not json_match:
                print(f"Error: No JSON found in LLM text fallback: {raw_output}")
                return None

            json_string = json_match.group(0)
            return json.loads(json_string)
        except Exception as fallback_e:
            print(f"LLM fallback error: {fallback_e}")
            return None