# agents/quiz.py
from utils.llm_clients import get_json_response_from_llm
from utils.prompts import QUIZ_PROMPT
from utils.database import add_topic_and_quizzes # <-- IMPORT DB FUNCTION
import json
import os

class QuizAgent:
    """
    Generates MCQs and saves them to the central database
    to enable performance tracking.
    """
    def __init__(self):
        print("QuizAgent: Initialized.")

    def generate_and_store_quizzes(self, text_chunks):
        """
        Generates quizzes and saves them to the DB, linked to their chunk.
        """
        print(f"QuizAgent: Generating and storing quizzes for {len(text_chunks)} chunks...")
        
        total_quizzes = 0
        for chunk in text_chunks:
            prompt = QUIZ_PROMPT.format(text_chunk=chunk)
            response_json = get_json_response_from_llm(prompt)
            
            if response_json and isinstance(response_json, list):
                # Add this chunk and its quizzes to the database
                add_topic_and_quizzes(chunk, response_json)
                total_quizzes += len(response_json)
        
        print(f"QuizAgent: Generated and stored {total_quizzes} quizzes in the database.")
        return total_quizzes