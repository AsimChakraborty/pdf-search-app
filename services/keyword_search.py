"""
Keyword Search Service
SQLite-based full-text and LIKE search
"""
import sqlite3
import re
from typing import List, Dict, Any

# Setup logging
from .log_config import get_logger
logger = get_logger(__name__)

DATABASE = 'database/pdf_index.db'


def search_keyword(query: str, limit: int = 20, match_all: bool = False) -> List[Dict[str, Any]]:
    """
    Search using SQLite LIKE (case-insensitive).
    Works with concatenated words in PDF text.
    
    Args:
        query: Search query string
        limit: Maximum results
        match_all: If True, require ALL words to match (AND). If False, any word (OR).
    
    Returns:
        List of results with filename, page_number, snippet, and relevance score
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    original_query = query.strip()
    query_lower = original_query.lower()
    words = [w.strip() for w in query_lower.split() if w.strip()]
    
    if not words:
        return []
    
    try:
        like_patterns = [f'%{w}%' for w in words]
        
        if len(words) == 1:
            where_clause = 'LOWER(content) LIKE ?'
            params = like_patterns + [limit]
            snippet_query = 'substr(pc.content, INSTR(LOWER(pc.content), ?), 250)'
            snippet_params = words[0]
        else:
            if match_all:
                # AND: all words must match
                conditions = ['LOWER(content) LIKE ?' for _ in words]
                where_clause = ' AND '.join(conditions)
            else:
                # OR: any word matches
                conditions = ['LOWER(content) LIKE ?' for _ in words]
                where_clause = ' OR '.join(conditions)
            
            snippet_query = 'substr(pc.content, INSTR(LOWER(pc.content), ?), 250)'
            snippet_params = words[0]
            params = like_patterns + [limit]
        
        search_sql = f'''SELECT p.filename, pc.page_number, pc.content,
            {snippet_query} as snippet
            FROM pdf_content pc
            JOIN pdfs p ON pc.pdf_id = p.id
            WHERE {where_clause}
            ORDER BY p.filename, pc.page_number
            LIMIT ?'''
        
        if len(words) == 1:
            cursor.execute(search_sql, like_patterns + params)
        else:
            cursor.execute(search_sql, [snippet_params] + params)
        
        results = cursor.fetchall()
        
        # Group by filename with unique pages
        grouped = {}
        for filename, page_number, content, snippet in results:
            if filename not in grouped:
                grouped[filename] = {
                    'filename': filename, 
                    'pages': [],
                    'content': content  # Store full content for relevance calc
                }
            
            existing_pages = [p['page_number'] for p in grouped[filename]['pages']]
            if page_number not in existing_pages:
                # Calculate keyword relevance score
                content_lower = content.lower()
                
                # Count exact word matches
                matched_words = sum(1 for w in words if w in content_lower)
                
                # Calculate relevance: matched words / total words (normalized)
                relevance = matched_words / len(words) if words else 0
                
                # Bonus for exact phrase match
                if original_query.lower() in content_lower:
                    relevance = min(1.0, relevance + 0.3)
                
                # Highlight each word in the snippet
                marked_snippet = snippet
                for word in words:
                    if word:
                        pattern = re.compile(re.escape(word), re.IGNORECASE)
                        marked_snippet = pattern.sub(f'<mark>{word}</mark>', marked_snippet)
                
                grouped[filename]['pages'].append({
                    'page_number': page_number, 
                    'snippet': marked_snippet,
                    'relevance': round(relevance, 4)
                })
        
        return list(grouped.values())
    
    except Exception as e:
        logger.error(f"Keyword search error: {e}", exc_info=True)
        return []
    finally:
        conn.close()