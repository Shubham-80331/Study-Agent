# agents/doubt_agent.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from utils.prompts import DOUBT_PROMPT
from utils.llm_clients import model # <-- Import the configured Gemini model
import os

VECTOR_STORE_PATH = "vector_store/study_material.index"
CHUNKS_PATH = "vector_store/chunks.pkl"

class DoubtAgent:
    """
    Answers contextual doubts using RAG with a Gemini model.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.embedding_model = SentenceTransformer(model_name)
        try:
            self.vector_store = faiss.read_index(VECTOR_STORE_PATH)
            with open(CHUNKS_PATH, 'rb') as f:
                self.text_chunks = pickle.load(f)
            print("DoubtAgent: Initialized and loaded vector store.")
        except Exception as e:
            print(f"DoubtAgent: Error loading vector store. Has it been created? {e}")
            self.vector_store = None
            self.text_chunks = []

    def answer_question(self, query):
        if not self.vector_store:
            return "The study material has not been processed yet. Please upload a PDF first."
        if not model:
             return "The Gemini LLM model is not initialized. Please check your API key."

        print(f"DoubtAgent: Answering query: {query}")
        
        # 1. Retrieve relevant chunks
        context_chunks = self._retrieve_context(query)
        context = "\n\n".join(context_chunks)
        
        # 2. Generate answer
        prompt = DOUBT_PROMPT.format(context=context, query=query)
        
        # --- This block is now for Gemini ---
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.1)
            )
            answer = response.text
            return answer
        except Exception as e:
            print(f"Error in DoubtAgent LLM call (Gemini): {e}")
            return "Sorry, I encountered an error trying to answer your question."
        # --- End Gemini block ---

    def _retrieve_context(self, query, k=3):
        """Finds the top-k most relevant text chunks."""
        query_embedding = self.embedding_model.encode([query]).astype('float32')
        distances, indices = self.vector_store.search(query_embedding, k)
        
        retrieved_chunks = [self.text_chunks[i] for i in indices[0]]
        return retrieved_chunks