"""Text embedding service using sentence-transformers."""
from typing import List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize embedding model."""
        self.model_name = model_name
        self._model = None
    
    @property
    def model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.model.get_sentence_embedding_dimension()
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


# Global singleton
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(model_name: Optional[str] = None) -> EmbeddingService:
    """Get or create embedding service singleton."""
    global _embedding_service
    
    if _embedding_service is None:
        from .config import get_settings
        settings = get_settings()
        model = model_name or settings.embedding_model
        _embedding_service = EmbeddingService(model)
    
    return _embedding_service
