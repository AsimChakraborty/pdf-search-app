"""
Hybrid Search Service
Combines keyword and semantic search with ranking
"""
from typing import List, Dict, Any
from . import keyword_search
from . import semantic_search


def search_hybrid(query: str, limit: int = 20, keyword_weight: float = 0.5) -> List[Dict[str, Any]]:
    """
    Combine keyword and semantic search results.
    
    Args:
        query: Search query
        limit: Maximum results
        keyword_weight: Weight for keyword results (0-1). 
                       Semantic weight = 1 - keyword_weight
    
    Returns:
        Combined and ranked results from both searches
    """
    # Get results from both search methods
    keyword_results = keyword_search.search_keyword(query, limit * 2)
    semantic_results = semantic_search.search_semantic(query, limit * 2)
    
    # Score and combine results
    combined = {}
    
    # Add keyword results with scores
    for doc in keyword_results:
        filename = doc['filename']
        if filename not in combined:
            combined[filename] = {
                'filename': filename,
                'pages': [],
                'keyword_score': 0,
                'semantic_score': 0,
                'keyword_matches': 0,
                'semantic_matches': 0
            }
        
        combined[filename]['keyword_matches'] += len(doc['pages'])
        
        # Calculate average relevance from all pages - use actual relevance score now
        page_relevances = [p.get('relevance', 0) for p in doc['pages']]
        avg_relevance = sum(page_relevances) / len(page_relevances) if page_relevances else 0
        
        # Use the actual relevance score, not a fixed 1.0
        combined[filename]['keyword_score'] = max(combined[filename]['keyword_score'], avg_relevance)
        
        for page in doc['pages']:
            page_number = page['page_number']
            
            # Check if page already exists
            existing_idx = None
            for i, p in enumerate(combined[filename]['pages']):
                if p['page_number'] == page_number:
                    existing_idx = i
                    break
            
            if existing_idx is None:
                combined[filename]['pages'].append({
                    'page_number': page_number,
                    'snippet': page.get('snippet', ''),
                    'keyword_match': True,
                    'semantic_match': False
                })
    
    # Add semantic results with scores
    for doc in semantic_results:
        filename = doc['filename']
        if filename not in combined:
            combined[filename] = {
                'filename': filename,
                'pages': [],
                'keyword_score': 0,
                'semantic_score': 0,
                'keyword_matches': 0,
                'semantic_matches': 0
            }
        
        combined[filename]['semantic_matches'] += len(doc['pages'])
        
        for page in doc['pages']:
            page_number = page['page_number']
            
            # Get snippet (either from semantic or fallback to page object)
            snippet = page.get('snippet', '')
            
            # Get similarity score
            similarity = page.get('similarity', 0)
            
            # Update semantic score with max similarity
            if similarity > combined[filename]['semantic_score']:
                combined[filename]['semantic_score'] = similarity
            
            # Check if page already exists
            existing_idx = None
            for i, p in enumerate(combined[filename]['pages']):
                if p['page_number'] == page_number:
                    existing_idx = i
                    break
            
            if existing_idx is not None:
                # Update existing page with semantic info
                combined[filename]['pages'][existing_idx]['semantic_match'] = True
                combined[filename]['pages'][existing_idx]['similarity'] = similarity
            else:
                # Add new page
                combined[filename]['pages'].append({
                    'page_number': page_number,
                    'snippet': snippet,
                    'keyword_match': False,
                    'semantic_match': True,
                    'similarity': similarity
                })
    
    # Calculate final scores and format results
    final_results = []
    
    for filename, data in combined.items():
        # Calculate weighted score using actual relevance scores (not just binary)
        keyword_score = data['keyword_score']
        semantic_score = data['semantic_score']
        
        # Count pages that match both keyword AND semantic (higher quality matches)
        matching_pages = sum(1 for p in data['pages'] if p.get('keyword_match') and p.get('semantic_match'))
        
        final_score = (keyword_score * keyword_weight + 
                      semantic_score * (1 - keyword_weight))
        
        # Add small bonus for pages that match both ways (more relevant)
        if matching_pages > 0:
            final_score = min(1.0, final_score + (matching_pages * 0.05))
        
        # Filter pages: prioritize keyword matches, then include semantic ones with caution
        # For hybrid search, show pages with keyword matches first
        keyword_pages = [p for p in data['pages'] if p.get('keyword_match')]
        semantic_only_pages = [p for p in data['pages'] if not p.get('keyword_match') and p.get('semantic_match')]
        
        # Only include semantic-only pages if there are no keyword matches
        if keyword_pages:
            display_pages = keyword_pages
        else:
            # Show semantic pages only if no keyword matches exist
            display_pages = data['pages']
        
        # Create final result - only show essential info
        result = {
            'filename': filename,
            'pages': sorted(display_pages, key=lambda x: x['page_number'])
        }
        
        # Only add score if not purely keyword-based
        if semantic_only_pages and keyword_pages:
            result['score'] = round(final_score, 4)
        
        final_results.append(result)
    
    # Sort by score (highest first)
    final_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Limit results
    return final_results[:limit]


def search_all_types(query: str, limit: int = 20) -> Dict[str, Any]:
    """
    Execute all three search types and return combined results.
    Useful for comparison.
    """
    keyword_results = keyword_search.search_keyword(query, limit)
    semantic_results = semantic_search.search_semantic(query, limit)
    hybrid_results = search_hybrid(query, limit)
    
    return {
        'keyword': {
            'results': keyword_results,
            'total_documents': len(keyword_results)
        },
        'semantic': {
            'results': semantic_results,
            'total_documents': len(semantic_results)
        },
        'hybrid': {
            'results': hybrid_results,
            'total_documents': len(hybrid_results)
        }
    }