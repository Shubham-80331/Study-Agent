# app.py
import streamlit as st
import json
import os
import pandas as pd
from main import run_study_pipeline, UPLOAD_DIR
from agents.doubt_agent import DoubtAgent
from agents.planner import PlannerAgent
from utils.database import get_all_quizzes_for_ui, record_quiz_result, DB_FILE

# File paths for outputs
FLASHCARD_FILE = "outputs/flashcards.json"
PLAN_FILE = "outputs/planner.json"

st.set_page_config(layout="wide")
st.title("🧠 Autonomous Study Workflow Agent (Full Version)")

# --- 1. PDF UPLOAD ---
st.subheader("1. Upload Your Study Material")
uploaded_file = st.file_uploader("Upload Your Notes (PDF, Scans, Text)", type="pdf")

if uploaded_file:
    st.write(f"File '{uploaded_file.name}' uploaded successfully!")
    
    # Save the file to a known path
    temp_pdf_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Generate Study Materials"):
        with st.spinner("Your AI agents are hard at work... Reading (with OCR), creating flashcards, building quizzes, and planning your revision..."):
            success = run_study_pipeline(temp_pdf_path)
        
        if success:
            st.success("Your study materials are ready!")
            # Initialize the DoubtAgent in session state after processing
            st.session_state.doubt_agent = DoubtAgent()
            st.session_state.quizzes = get_all_quizzes_for_ui()
            st.rerun()
        else:
            st.error("There was an error processing your file. Please try again.")

# --- 2. DISPLAY TABS ---
st.subheader("2. Your Generated Study Hub")

# Check if DB exists to show tabs
if not os.path.exists(DB_FILE):
    st.info("Upload a PDF and click 'Generate' to see your materials.")
else:
    # Initialize agents and quiz data if not already in state
    if 'doubt_agent' not in st.session_state:
        st.session_state.doubt_agent = DoubtAgent()
    if 'quizzes' not in st.session_state:
        st.session_state.quizzes = get_all_quizzes_for_ui()

    tab1, tab2, tab3, tab4 = st.tabs(["❓ Ask a Doubt", "💡 Flashcards", "📝 Smart Quiz", "🗓️ Smart Revision Plan"])

    # --- DOUBT AGENT TAB ---
    with tab1:
        st.header("Ask a Question About Your Notes")
        query = st.text_input("What concept do you need clarified?", key="doubt_query")
        
        if query:
            with st.spinner("Finding the answer in your notes..."):
                answer = st.session_state.doubt_agent.answer_question(query)
                st.markdown(answer)

    # --- FLASHCARD TAB (from hint) ---
    with tab2:
        st.header("Generated Flashcards")
        try:
            with open(FLASHCARD_FILE) as f:
                cards = json.load(f)
            
            if 'card_index' not in st.session_state:
                st.session_state.card_index = 0
            
            if not cards:
                st.warning("No flashcards were generated.")
            else:
                card = cards[st.session_state.card_index]
                
                with st.container(border=True):
                    if 'show_answer' not in st.session_state:
                        st.session_state.show_answer = False
                    
                    st.markdown(f"**Q:** {card['question']}")
                    
                    if st.button("Show Answer", key=f"show_{st.session_state.card_index}"):
                        st.session_state.show_answer = not st.session_state.show_answer
                    
                    if st.session_state.show_answer:
                        st.markdown(f"**A:** {card['answer']}")
                
                col1, col2, col3 = st.columns([1,1,1])
                with col1:
                    if st.button("⬅️ Previous") and st.session_state.card_index > 0:
                        st.session_state.card_index -= 1
                        st.session_state.show_answer = False
                        st.rerun()
                with col3:
                    if st.button("Next ➡️") and st.session_state.card_index < len(cards) - 1:
                        st.session_state.card_index += 1
                        st.session_state.show_answer = False
                        st.rerun()
                
                st.markdown(f"Card {st.session_state.card_index + 1} of {len(cards)}")

        except Exception as e:
            st.error(f"Could not load flashcards: {e}")

    # --- QUIZ TAB (Smart) ---
    with tab3:
        st.header("Smart Quiz")
        st.write("Your answers here will update your Smart Revision Plan!")
        
        quizzes = st.session_state.quizzes
        if not quizzes:
            st.warning("No quiz questions were found in the database.")
        else:
            with st.form("quiz_form"):
                user_answers = {}
                for i, q in enumerate(quizzes):
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    # Use question ID as the key
                    user_answers[q['id']] = st.radio("Choose one:", q['options'], key=f"quiz_{q['id']}", index=None)
                    st.markdown("---")
                
                submitted = st.form_submit_button("Submit Quiz")

            if submitted:
                correct_count = 0
                total_count = len(quizzes)
                
                for q_id, user_choice in user_answers.items():
                    # Find the correct answer from our quiz list
                    correct_answer = next(q['answer'] for q in quizzes if q['id'] == q_id)
                    is_correct = (user_choice == correct_answer)
                    
                    if is_correct:
                        correct_count += 1
                    
                    # Record the result in the database
                    record_quiz_result(q_id, is_correct)
                
                st.success(f"Quiz Submitted! You got {correct_count} out of {total_count} correct.")
                st.info("Your performance has been saved. Your Revision Plan will be updated next time you generate it.")

    # --- PLANNER TAB (Smart) ---
    with tab4:
        st.header("Your Smart Revision Plan")
        st.write("This plan prioritizes topics based on your quiz performance (worst topics first).")
        
        if st.button("Refresh Revision Plan"):
            with st.spinner("Updating plan based on your latest quiz results..."):
                planner = PlannerAgent()
                planner.generate_smart_plan()
                st.rerun()

        try:
            with open(PLAN_FILE) as f:
                plan = json.load(f)
            
            if not plan:
                st.warning("No revision plan was generated.")
            else:
                df = pd.DataFrame(plan)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load plan: {e}")