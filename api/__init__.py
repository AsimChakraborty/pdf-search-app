"""
API Package - Flask routes
"""
from .pdf_routes import pdf_bp
from .search_routes import search_bp

__all__ = ['pdf_bp', 'search_bp']