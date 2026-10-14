"""
Embedding Service using Sentence Transformers
Generates text embeddings for semantic search
"""
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional

# Model name from docs
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# Singleton model instance
_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get or create the singleton embedding model.
    Model is loaded once and reused for better performance.
    """
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Embedding model loaded successfully!")
    return _model


def generate_embedding(text: str) -> np.ndarray:
    """
    Generate embedding vector for a text string.
    
    Args:
        text: Input text
    
    Returns:
        Numpy array with embedding vector
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding


def generate_embeddings_batch(texts: list) -> np.ndarray:
    """
    Generate embeddings for multiple texts at once (more efficient).
    
    Args:
        texts: List of text strings
    
    Returns:
        Numpy array with embeddings for all texts
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return embeddings


def get_embedding_dimension() -> int:
    """
    Get the dimension of embedding vectors.
    all-MiniLM-L6-v2 produces 384-dimensional vectors.
    """
    return 384