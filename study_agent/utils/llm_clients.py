# utils/llm_clients.py
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv  

load_dotenv()  

# --- OPTION 2: Google Gemini (NOW ACTIVE) ---
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Have you created a .env file?")
        
    genai.configure(api_key=api_key)
    # --- THIS LINE IS THE FIX for Error 1 ---
    model = genai.GenerativeModel('gemini-pro') 
    
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
        
    # --- We also remove JSON mode, as gemini-pro is less reliable with it ---
    try:
        response = model.generate_content(prompt)
        raw_output = response.text
        
        # Clean the output to find the JSON
        json_match = re.search(r'\[.*\]|\{.*\}', raw_output, re.DOTALL)
        
        if not json_match:
            print(f"Error: No JSON found in LLM response: {raw_output}")
            return None

        json_string = json_match.group(0)
        return json.loads(json_string)

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from LLM response: {raw_output}")
        return None
    except Exception as e:
        print(f"An error occurred calling LLM: {e}")
        return None
