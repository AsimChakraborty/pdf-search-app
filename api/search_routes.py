"""
Search API Routes
Handles search operations (keyword, semantic, hybrid)
"""
from flask import Blueprint, request, jsonify

# Services
from services.keyword_search import search_keyword
from services.semantic_search import search_semantic
from services.hybrid_search import search_hybrid, search_all_types

# Setup logging
from services.log_config import get_logger
logger = get_logger(__name__)

# Create blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api')


@search_bp.route('/search', methods=['GET'])
def search():
    """Main search endpoint"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'hybrid').lower()
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'error': 'Query is required', 'results': []}), 400
    
    logger.info(f"Search request: query='{query}', type={search_type}, limit={limit}")
    
    try:
        if search_type == 'keyword':
            results = search_keyword(query, limit)
        elif search_type == 'semantic':
            results = search_semantic(query, limit)
        elif search_type == 'hybrid':
            results = search_hybrid(query, limit)
        else:
            return jsonify({'error': f'Invalid search type: {search_type}'}), 400
        
        logger.info(f"Search completed: {search_type} found {len(results)} documents for query '{query}'")
        
        return jsonify({
            'query': query,
            'search_type': search_type,
            'results': results,
            'total_documents': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'results': []}), 500


@search_bp.route('/search/all', methods=['GET'])
def search_all():
    """Search all types at once"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    logger.info(f"Search all request: query='{query}', limit={limit}")
    
    try:
        results = search_all_types(query, limit)
        return jsonify({
            'query': query,
            'results': results
        })
    except Exception as e:
        logger.error(f"Search all error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500