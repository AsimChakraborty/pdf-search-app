"""Hybrid Search - Keyword only with highlighting"""
from typing import List, Dict, Any
from . import keyword_search

def search_hybrid(query: str, limit: int = 20, keyword_weight: float = 0.5) -> List[Dict[str, Any]]:
    keyword_results = keyword_search.search_keyword(query, limit)
    final_results = []
    for doc in keyword_results:
        pages = []
        for page in doc.get("pages", []):
            pages.append({
                "page_number": page["page_number"],
                "snippet": page.get("snippet", ""),
                "keyword_match": True,
                "relevance": page.get("relevance", 0)
            })
        if pages:
            result = {
                "filename": doc["filename"],
                "pages": sorted(pages, key=lambda x: x["page_number"]),
                "score": max((p.get("relevance", 0) for p in pages), default=0)
            }
            final_results.append(result)
    return final_results[:limit]

def search_all_types(query: str, limit: int = 20) -> Dict[str, Any]:
    kw = keyword_search.search_keyword(query, limit)
    return {
        "keyword": {"results": kw, "total_documents": len(kw)},
        "semantic": {"results": kw, "total_documents": len(kw)},
        "hybrid": {"results": search_hybrid(query, limit), "total_documents": len(kw)}
    }