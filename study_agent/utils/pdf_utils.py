# utils/pdf_utils.py
import fitz  # PyMuPDF
import re
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF, automatically applying OCR to scanned pages.
    Implements the "Supports both text and image-based documents" feature.
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    print(f"PDF Utils: Processing {len(doc)} pages...")

    for page_num, page in enumerate(doc):
        # 1. Try to get text directly
        page_text = page.get_text().strip()
        
        # 2. Check if text is meaningful (heuristic)
        if len(page_text) < 100:  # Threshold for considering a page "scanned"
            print(f"PDF Utils: Page {page_num+1} seems to be a scan. Running OCR...")
            try:
                # 3. If no text, render page as image and use OCR
                pix = page.get_pixmap(dpi=300)  # High DPI for better OCR
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # 4. Use Pytesseract to extract text
                ocr_text = pytesseract.image_to_string(img)
                page_text = ocr_text
            except Exception as e:
                print(f"PDF Utils: OCR failed for page {page_num+1}: {e}")
                page_text = ""  # Failed OCR, add no text
        
        full_text += page_text + "\n\n" # Add page break
    
    doc.close()
    
    # Clean up common PDF/OCR artifacts
    full_text = re.sub(r'\s*\n\s*', '\n', full_text) # Consolidate multiple newlines
    full_text = re.sub(r'(\w)-\n(\w)', r'\1\2', full_text) # Fix hyphenated word breaks
    
    print(f"PDF Utils: Extraction complete. Total characters: {len(full_text)}")
    return full_text.encode('utf-8').decode('utf-8')

def chunk_text(text, min_chunk_size=100):
    """Splits text into meaningful chunks."""
    # Split by double newlines (paragraphs)
    chunks = text.split("\n\n")
    
    # Clean, strip, and filter chunks
    cleaned_chunks = [c.strip() for c in chunks if len(c.strip()) > min_chunk_size]
    
    # If no good chunks found, try a simpler split
    if not cleaned_chunks and text:
        chunks = text.split("\n")
        cleaned_chunks = [c.strip() for c in chunks if len(c.strip()) > min_chunk_size]

    return cleaned_chunks