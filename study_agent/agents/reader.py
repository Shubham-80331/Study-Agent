# agents/reader.py
from utils.pdf_utils import extract_text_from_pdf, chunk_text
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

VECTOR_STORE_PATH = "vector_store/study_material.index"
CHUNKS_PATH = "vector_store/chunks.pkl"

class ReaderAgent:
    """
    Reads, cleans text (with OCR), and creates vector embeddings for RAG.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.text_chunks = []
        self.embedding_model = SentenceTransformer(model_name)
        self.vector_store = None
        print("ReaderAgent: Initialized.")

    def process_pdf(self, pdf_path):
        """
        Main workflow for the agent.
        """
        print(f"ReaderAgent: Processing {pdf_path}...")
        
        # 1. Extract text (now with OCR)
        raw_text = extract_text_from_pdf(pdf_path)
        
        # 2. Process and chunk text
        self.text_chunks = chunk_text(raw_text)
        
        if not self.text_chunks:
            print("ReaderAgent: No text chunks found. Aborting.")
            return False
        
        print(f"ReaderAgent: Extracted {len(self.text_chunks)} text chunks.")
        
        # 3. Create vector embeddings (for Doubt Agent)
        self._create_vector_store()
        
        return self.text_chunks

    def _create_vector_store(self):
        """Creates and saves a FAISS vector store."""
        print("ReaderAgent: Creating vector embeddings...")
        embeddings = self.embedding_model.encode(self.text_chunks, show_progress_bar=True)
        
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatL2(dimension)
        self.vector_store.add(np.array(embeddings).astype('float32'))
        
        # Save the vector store and chunks
        os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
        faiss.write_index(self.vector_store, VECTOR_STORE_PATH)
        
        with open(CHUNKS_PATH, 'wb') as f:
            pickle.dump(self.text_chunks, f)
            
        print(f"ReaderAgent: Vector store and chunks saved.")