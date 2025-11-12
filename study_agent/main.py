# main.py
from agents.reader import ReaderAgent
from agents.flashcard import FlashcardAgent
from agents.quiz import QuizAgent
from agents.planner import PlannerAgent
from utils.database import initialize_database # <-- IMPORT
import time
import os

# Define a temporary path for the uploaded file
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def run_study_pipeline(pdf_path):
    """
    Executes the full multi-agent pipeline.
    """
    print("--- STARTING STUDY PIPELINE ---")
    start_time = time.time()
    
    # 0. Initialize Database
    initialize_database() # <-- ADD THIS STEP
    
    # 1. Reader Agent (with OCR)
    reader = ReaderAgent()
    text_chunks = reader.process_pdf(pdf_path)
    
    if not text_chunks:
        print("Pipeline Error: No text chunks extracted.")
        return False
    
    # 2. Flashcard Agent
    flashcard_agent = FlashcardAgent()
    flashcard_agent.generate_flashcards(text_chunks)
    
    # 3. Quiz Agent (saves to DB)
    quiz_agent = QuizAgent()
    quiz_agent.generate_and_store_quizzes(text_chunks)
    
    # 4. Planner Agent (reads from DB)
    planner_agent = PlannerAgent()
    planner_agent.generate_smart_plan()
    
    end_time = time.time()
    print(f"--- PIPELINE FINISHED IN {end_time - start_time:.2f} SECONDS ---")
    return True

if __name__ == "__main__":
    # This allows testing the pipeline from the command line
    print("Running test pipeline...")
    if os.path.exists("test.pdf"):
        run_study_pipeline("test.pdf")
    else:
        print("Please add a 'test.pdf' to the root folder to run a test.")