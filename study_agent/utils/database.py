# utils/database.py
import sqlite3
import os
import datetime

DB_FILE = "vector_store/study_data.db"
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """
    Creates the necessary tables if they don't exist.
    We'll link quizzes to the text chunks they were generated from.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Stores the original text chunks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_hash TEXT UNIQUE,
        content TEXT,
        last_revised DATE,
        revision_score REAL DEFAULT 0.0,
        revision_count INTEGER DEFAULT 0
    )
    """)
    
    # Stores quiz questions and tracks performance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        question TEXT,
        options TEXT, -- Storing options as a JSON string
        answer TEXT,
        correct_count INTEGER DEFAULT 0,
        incorrect_count INTEGER DEFAULT 0,
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Database: Initialized successfully.")

def add_topic_and_quizzes(chunk_content, quiz_list):
    """
    Adds a new topic (chunk) and its associated quizzes to the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use a hash to prevent duplicate chunks
    chunk_hash = str(hash(chunk_content))
    
    try:
        cursor.execute("INSERT OR IGNORE INTO topics (chunk_hash, content) VALUES (?, ?)", (chunk_hash, chunk_content))
        
        # Get the ID of the topic (either newly inserted or existing)
        cursor.execute("SELECT id FROM topics WHERE chunk_hash = ?", (chunk_hash,))
        topic_id_row = cursor.fetchone()
        if not topic_id_row:
             conn.close()
             return # Should not happen, but as a safeguard
        
        topic_id = topic_id_row['id']

        for quiz in quiz_list:
            # Check if this specific question already exists for this topic
            cursor.execute("SELECT id FROM quizzes WHERE topic_id = ? AND question = ?", (topic_id, quiz['question']))
            if cursor.fetchone() is None:
                # Store options as a JSON string
                options_json = json.dumps(quiz['options'])
                cursor.execute(
                    "INSERT INTO quizzes (topic_id, question, options, answer) VALUES (?, ?, ?, ?)",
                    (topic_id, quiz['question'], options_json, quiz['answer'])
                )
        
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Database Error: {e}")
        pass
    finally:
        conn.close()

def record_quiz_result(question_id, is_correct):
    """
    Records the outcome of a single quiz question.
    This is the core of "performance tracking".
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_correct:
        query = "UPDATE quizzes SET correct_count = correct_count + 1 WHERE id = ?"
    else:
        query = "UPDATE quizzes SET incorrect_count = incorrect_count + 1 WHERE id = ?"
    
    cursor.execute(query, (question_id,))
    
    # Also update the parent topic's 'last_revised' date
    cursor.execute("""
        UPDATE topics 
        SET last_revised = ? 
        WHERE id = (SELECT topic_id FROM quizzes WHERE id = ?)
    """, (datetime.date.today(), question_id))

    conn.commit()
    conn.close()

def get_all_quizzes_for_ui():
    """Fetches all quizzes for the Streamlit UI."""
    conn = get_db_connection()
    cursor = conn.cursor()
    quizzes = cursor.execute("""
        SELECT id, question, options, answer 
        FROM quizzes
    """).fetchall()
    conn.close()
    
    # Parse the JSON options string back into a list
    quiz_list = []
    for q in quizzes:
        quiz_list.append({
            'id': q['id'],
            'question': q['question'],
            'options': json.loads(q['options']),
            'answer': q['answer']
        })
    return quiz_list

def get_topics_for_revision():
    """
    This is the "smart" part.
    It fetches topics, prioritizing those with the worst performance.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate a 'priority_score'
    # Prioritizes:
    # 1. High incorrect_count
    # 2. Low correct_count
    # 3. Topics that haven't been quizzed (incorrect_count = 0 and last_revised is NULL)
    query = """
    SELECT 
        t.id, 
        t.content,
        t.last_revised,
        COALESCE(SUM(q.incorrect_count), 0) as total_incorrect,
        COALESCE(SUM(q.correct_count), 0) as total_correct
    FROM topics t
    LEFT JOIN quizzes q ON t.id = q.topic_id
    GROUP BY t.id
    ORDER BY total_incorrect DESC, total_correct ASC, t.last_revised ASC
    LIMIT 10 
    """
    
    topics = cursor.execute(query).fetchall()
    conn.close()
    return topics