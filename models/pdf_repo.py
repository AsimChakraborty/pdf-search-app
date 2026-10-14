"""
PDF Repository - PDF-specific database operations
Handles all PDF-related database queries
"""
from typing import List, Dict, Any, Optional
from .db import get_db_connection

# Setup logging
from services.log_config import get_logger
logger = get_logger(__name__)


def insert_pdf(filename: str, filepath: str) -> int:
    """Insert a new PDF record and return its ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO pdfs (filename, filepath) VALUES (?, ?)',
        (filename, filepath)
    )
    pdf_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.debug(f"Inserted PDF: {filename} with ID: {pdf_id}")
    return pdf_id


def get_all_pdfs() -> List[Dict[str, Any]]:
    """Get all uploaded PDFs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, filename, filepath, upload_date FROM pdfs ORDER BY upload_date DESC'
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row['id'],
            'filename': row['filename'],
            'filepath': row['filepath'],
            'upload_date': row['upload_date']
        }
        for row in rows
    ]


def get_pdf_by_id(pdf_id: int) -> Optional[Dict[str, Any]]:
    """Get a PDF by its ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, filepath, upload_date FROM pdfs WHERE id = ?', (pdf_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row['id'],
            'filename': row['filename'],
            'filepath': row['filepath'],
            'upload_date': row['upload_date']
        }
    return None


def delete_pdf(pdf_id: int) -> bool:
    """Delete a PDF and its content"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get file path before deleting
    cursor.execute('SELECT filepath FROM pdfs WHERE id = ?', (pdf_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False
    
    filepath = row['filepath']
    
    # Delete content first (due to foreign key)
    cursor.execute('DELETE FROM pdf_content WHERE pdf_id = ?', (pdf_id,))
    cursor.execute('DELETE FROM pdfs WHERE id = ?', (pdf_id,))
    
    conn.commit()
    conn.close()
    logger.info(f"Deleted PDF ID: {pdf_id}")
    return filepath


def insert_pdf_content(pdf_id: int, filename: str, page_number: int, content: str) -> None:
    """Insert extracted text content for a page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO pdf_content (pdf_id, filename, page_number, content) VALUES (?, ?, ?, ?)',
        (pdf_id, filename, page_number, content)
    )
    conn.commit()
    conn.close()


def get_pdf_content_by_pdf_id(pdf_id: int) -> List[Dict[str, Any]]:
    """Get all content for a specific PDF"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT page_number, content FROM pdf_content WHERE pdf_id = ? ORDER BY page_number',
        (pdf_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'page_number': row['page_number'],
            'content': row['content']
        }
        for row in rows
    ]


def get_all_pdf_content() -> List[Dict[str, Any]]:
    """Get all PDF content for indexing"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.filename, pc.page_number, pc.content 
        FROM pdf_content pc
        JOIN pdfs p ON pc.pdf_id = p.id
        ORDER BY p.id, pc.page_number
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'pdf_id': row['id'],
            'filename': row['filename'],
            'page_number': row['page_number'],
            'content': row['content']
        }
        for row in rows
    ]