"""
Database connection and initialization
Provides SQLite connection handling
"""
import sqlite3
import os
from pathlib import Path

# Setup logging
from services.log_config import get_logger
logger = get_logger(__name__)

# Database paths
BASE_DIR = Path(__file__).parent.parent
DATABASE = BASE_DIR / 'database' / 'pdf_index.db'
CHROMA_DB_PATH = BASE_DIR / 'database' / 'chroma_db'


def get_db_connection():
    """Get SQLite database connection"""
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # PDFs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # PDF content table (for keyword search)
    # Check if table exists and has correct structure
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pdf_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT,
            FOREIGN KEY (pdf_id) REFERENCES pdfs (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at: {DATABASE}")
    
    # Ensure ChromaDB directory exists
    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)


# Initialize on import
init_database()