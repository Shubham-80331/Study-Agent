# agents/flashcard.py
from utils.llm_clients import get_json_response_from_llm
from utils.prompts import FLASHCARD_PROMPT
import json
import os

OUTPUT_PATH = "outputs/flashcards.json"

class FlashcardAgent:
    """
    Generates Q/A flashcards from text chunks.
    """
    def __init__(self):
        self.flashcards = []
        print("FlashcardAgent: Initialized.")

    def generate_flashcards(self, text_chunks):
        print(f"FlashcardAgent: Generating flashcards for {len(text_chunks)} chunks...")
        
        for chunk in text_chunks:
            prompt = FLASHCARD_PROMPT.format(text_chunk=chunk)
            response_json = get_json_response_from_llm(prompt)
            
            if response_json and isinstance(response_json, list):
                self.flashcards.extend(response_json)
        
        self._save_flashcards()
        print(f"FlashcardAgent: Generated {len(self.flashcards)} flashcards.")
        return self.flashcards

    def _save_flashcards(self):
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.flashcards, f, indent=2)