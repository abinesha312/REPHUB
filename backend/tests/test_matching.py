"""Test matching logic with mocked embeddings."""
import pytest
from backend.app.embeddings import EmbeddingService


def test_embedding_service_dimension():
    """Test that embedding service returns correct dimension."""
    # Note: This will download the model on first run
    service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
    
    dimension = service.get_dimension()
    assert dimension == 384


def test_embedding_text_returns_list():
    """Test that embedding returns a list of floats."""
    service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
    
    text = "Software Engineer with Python experience"
    embedding = service.embed_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)


def test_embedding_empty_text():
    """Test embedding empty text returns zero vector."""
    service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
    
    embedding = service.embed_text("")
    
    assert len(embedding) == 384
    assert all(x == 0.0 for x in embedding)


def test_similar_texts_have_similar_embeddings():
    """Test that semantically similar texts have similar embeddings."""
    service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
    
    text1 = "Python developer with machine learning experience"
    text2 = "Software engineer skilled in Python and ML"
    text3 = "Chef with culinary arts degree"
    
    emb1 = service.embed_text(text1)
    emb2 = service.embed_text(text2)
    emb3 = service.embed_text(text3)
    
    # Cosine similarity helper
    def cosine_similarity(a, b):
        import numpy as np
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_1_2 = cosine_similarity(emb1, emb2)
    sim_1_3 = cosine_similarity(emb1, emb3)
    
    # Similar texts should have higher similarity than dissimilar texts
    assert sim_1_2 > sim_1_3
    assert sim_1_2 > 0.5  # Should be reasonably similar


def test_batch_embedding():
    """Test batch embedding functionality."""
    service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
    
    texts = [
        "Python developer",
        "Java engineer",
        "Data scientist"
    ]
    
    embeddings = service.embed_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)
