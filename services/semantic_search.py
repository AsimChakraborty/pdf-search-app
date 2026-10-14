"""
Semantic Search Service using ChromaDB
AI-powered search using sentence embeddings
"""
import os
import sqlite3
import chromadb
from typing import List, Dict, Any, Optional
import numpy as np

from .embedding_service import generate_embedding, generate_embeddings_batch

DATABASE = 'database/pdf_index.db'
CHROMA_DB_PATH = 'database/chroma_db'

# Initialize ChromaDB client
_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Get or create the ChromaDB client.
    """
    global _client
    if _client is None:
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _client


def get_or_create_collection(force_recreate=False):
    """
    Get or create the PDF chunks collection.
    """
    client = get_chroma_client()
    
    # Try to get existing collection and delete it if force_recreate
    try:
        existing = client.get_collection(name="pdf_chunks")
        if force_recreate:
            client.delete_collection(name="pdf_chunks")
            return client.create_collection(
                name="pdf_chunks",
                metadata={"description": "PDF page chunks for semantic search"}
            )
        return existing
    except:
        pass
    
    return client.create_collection(
        name="pdf_chunks",
        metadata={"description": "PDF page chunks for semantic search"}
    )


def index_pdf_to_chroma(pdf_id: int, filename: str):
    """
    Index a PDF's content into ChromaDB for semantic search.
    Creates embeddings for each page's content.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get all pages for this PDF
    cursor.execute(
        'SELECT page_number, content FROM pdf_content WHERE pdf_id = ? ORDER BY page_number',
        (pdf_id,)
    )
    pages = cursor.fetchall()
    conn.close()
    
    if not pages:
        return 0
    
    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []
    
    for page_num, content in pages:
        # Create a unique ID
        doc_id = f"{filename}_page_{page_num}"
        ids.append(doc_id)
        documents.append(content)
        metadatas.append({
            "pdf_id": pdf_id,
            "filename": filename,
            "page_number": page_num
        })
    
    # Get collection and add documents
    collection = get_or_create_collection()
    
    # Generate embeddings
    print(f"Generating embeddings for {len(documents)} pages...")
    embeddings = generate_embeddings_batch(documents)
    
    # Add to ChromaDB
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )
    
    print(f"Indexed {len(pages)} pages to ChromaDB")
    return len(pages)


def search_semantic(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search using semantic similarity (AI-powered).
    Finds pages with similar meaning, not just keyword matches.
    
    Args:
        query: Natural language query
        limit: Maximum results
    
    Returns:
        List of results ranked by semantic similarity
    """
    collection = get_or_create_collection()
    
    if collection.count() == 0:
        return []
    
    # Generate embedding for query
    query_embedding = generate_embedding(query)
    
    # Search in ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=limit,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    formatted_results = []
    if results['ids'] and len(results['ids']) > 0:
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]
            distance = results['distances'][0][i]
            
            filename = metadata.get('filename', 'unknown')
            page_number = metadata.get('page_number', 0)
            
            # Create snippet around the matched content
            snippet = document[:250] if len(document) > 250 else document
            
            # Convert distance to similarity score (lower distance = higher similarity)
            # ChromaDB uses cosine distance - normalize to 0-1 range
            # Distance: 0 = identical, 2 = max difference (for cosine)
            distance = results['distances'][0][i]
            
            # Normalize: 0 distance = 1 similarity, 2 distance = 0 similarity
            similarity = max(0, 1 - (distance / 2))
            
            formatted_results.append({
                'filename': filename,
                'page_number': page_number,
                'snippet': snippet,
                'similarity': round(similarity, 4)
            })
    
    # Group by filename
    grouped = {}
    for result in formatted_results:
        filename = result['filename']
        if filename not in grouped:
            grouped[filename] = {'filename': filename, 'pages': []}
        
        # Check for duplicate pages
        existing_pages = [p['page_number'] for p in grouped[filename]['pages']]
        if result['page_number'] not in existing_pages:
            grouped[filename]['pages'].append({
                'page_number': result['page_number'],
                'snippet': result['snippet'],
                'similarity': result.get('similarity', 0)
            })
    
    return list(grouped.values())


def delete_pdf_from_chroma(pdf_id: int):
    """
    Remove a PDF's chunks from ChromaDB.
    """
    collection = get_or_create_collection()
    
    # Get all IDs for this PDF
    results = collection.get(where={"pdf_id": pdf_id})
    
    if results['ids']:
        collection.delete(ids=results['ids'])
        print(f"Deleted {len(results['ids'])} chunks from ChromaDB")


def rebuild_chroma_index():
    """
    Rebuild the entire ChromaDB index from SQLite.
    Use for migration or recovery.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get all PDFs
    cursor.execute('SELECT id, filename FROM pdfs')
    pdfs = cursor.fetchall()
    conn.close()
    
    # Get collection with recreate option
    collection = get_or_create_collection(force_recreate=True)
    
    # Re-index each PDF
    total_pages = 0
    for pdf_id, filename in pdfs:
        count = index_pdf_to_chroma(pdf_id, filename)
        total_pages += count
    
    print(f"Rebuilt ChromaDB index: {len(pdfs)} PDFs, {total_pages} pages")
    return total_pages