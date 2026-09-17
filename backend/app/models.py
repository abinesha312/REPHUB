"""Database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from .database import Base


class User(Base):
    """User model (simplified for demo)."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class Resume(Base):
    """Resume version model with vector embeddings."""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    format = Column(String(50), nullable=False)  # pdf, latex, doc, docx
    version = Column(Integer, nullable=False)  # 1, 2, 3, ...
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    content_type = Column(String(100))
    file_size = Column(Integer)
    
    # Extracted content
    extracted_text = Column(Text)
    
    # Vector embedding for similarity search
    embedding = Column(Vector(384))  # Dimension depends on model
    
    # Metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Resume(user={self.user_id}, format={self.format}, v{self.version})>"
