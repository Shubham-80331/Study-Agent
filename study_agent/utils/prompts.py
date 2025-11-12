# utils/prompts.py

FLASHCARD_PROMPT = """
You are a flashcard generator.
Create 5 question-answer pairs from the following text.
Return output *only* in a valid JSON list format.
Do not include any other text before or after the JSON.

Example Output:
[
  {"question": "What is an Operating System?", "answer": "Software that manages computer hardware and software resources."},
  {"question": "Name two types of OS.", "answer": "Batch OS, Real-time OS"}
]

Text:
---
{text_chunk}
---
"""

QUIZ_PROMPT = """
You are a quiz generator.
Make 3 multiple-choice questions from this text.
Each question must have 4 options and one correct answer.
Return output *only* in a valid JSON list format.

Example Output:
[
  {"question": "Which of the following is an OS?", "options": [ "Compiler", "Assembler", "Batch", "Linker"], "answer": "Batch"}
]

Text:
---
{text_chunk}
---
"""

DOUBT_PROMPT = """
You are a helpful study assistant.
Answer the user's question based *only* on the provided context.
If the answer is not in the context, say "I'm sorry, I don't have information on that topic from your notes."

Context:
---
{context}
---

Question: {query}

Answer:
"""