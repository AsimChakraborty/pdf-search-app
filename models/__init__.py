"""
Models Package - Database operations
Single source for all database connections and operations
"""
from .db import get_db_connection, init_database
from .pdf_repo import (
    insert_pdf,
    get_all_pdfs,
    get_pdf_by_id,
    delete_pdf,
    insert_pdf_content,
    get_pdf_content_by_pdf_id
)

__all__ = [
    'get_db_connection',
    'init_database',
    'insert_pdf',
    'get_all_pdfs',
    'get_pdf_by_id',
    'delete_pdf',
    'insert_pdf_content',
    'get_pdf_content_by_pdf_id'
]