"""
PDF Text Extraction Service
Improved text extraction with proper spacing and chunking
"""
import re
import pdfplumber
from typing import List, Dict, Any


def improve_text_spacing(text: str) -> str:
    """
    Fix common PDF extraction issues with word spacing.
    Adds spaces between concatenated words that should be separate.
    """
    if not text:
        return ""
    
    # Fix: Add space between word and capital letter (e.g., "wordWord" -> "word Word")
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Fix: Add space after periods that don't have one
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    
    # Fix: Add space after colons that don't have one  
    text = re.sub(r':([A-Z])', r': \1', text)
    
    # Fix: Add space after numbers followed by letters
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from PDF with improved formatting.
    Returns list of dicts with page_number and content.
    """
    pages_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text
                text = page.extract_text()
                
                if text and text.strip():
                    # Improve spacing
                    text = improve_text_spacing(text)
                    pages_data.append({
                        'page_number': page_num,
                        'content': text
                    })
                    
    except Exception as e:
        print(f'Error extracting PDF {pdf_path}: {e}')
    
    return pages_data


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Approximate words per chunk
        overlap: Number of overlapping words between chunks
    
    Returns:
        List of dicts with chunk_id and content
    """
    # Split into words
    words = text.split()
    
    if len(words) <= chunk_size:
        return [{'chunk_id': 0, 'content': text}]
    
    chunks = []
    start = 0
    chunk_id = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        
        chunks.append({
            'chunk_id': chunk_id,
            'content': chunk_text
        })
        
        # Move start position with overlap
        start = end - overlap
        chunk_id += 1
    
    return chunks


def extract_text_with_chunks(pdf_path: str, chunk_size: int = 500, overlap: int = 50) -> Dict[str, Any]:
    """
    Extract text from PDF and create chunks.
    
    Returns:
        Dict with 'pages' and 'chunks' lists
    """
    pages_data = extract_text_from_pdf(pdf_path)
    
    all_chunks = []
    for page in pages_data:
        page_chunks = chunk_text(page['content'], chunk_size, overlap)
        for chunk in page_chunks:
            all_chunks.append({
                'page_number': page['page_number'],
                'chunk_id': chunk['chunk_id'],
                'content': chunk['content']
            })
    
    return {
        'pages': pages_data,
        'chunks': all_chunks
    }