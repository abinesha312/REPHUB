"""Pydantic schemas for request/response models."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeUploadRequest(BaseModel):
    """Not used directly - multipart form data."""
    pass


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    format: str
    version: int
    filename: str
    storage_path: str
    content_type: Optional[str]
    file_size: Optional[int]
    uploaded_at: datetime
    has_embedding: bool = False
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_embedding(cls, obj):
        """Create response with embedding check."""
        data = {
            "id": obj.id,
            "user_id": obj.user_id,
            "format": obj.format,
            "version": obj.version,
            "filename": obj.filename,
            "storage_path": obj.storage_path,
            "content_type": obj.content_type,
            "file_size": obj.file_size,
            "uploaded_at": obj.uploaded_at,
            "has_embedding": obj.embedding is not None
        }
        return cls(**data)


class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    total: int


class MatchRequest(BaseModel):
    job_description: str = Field(..., min_length=10)
    user_id: Optional[int] = None
    limit: int = Field(default=10, ge=1, le=50)


class MatchResult(BaseModel):
    resume_id: int
    user_id: int
    format: str
    version: int
    filename: str
    similarity_score: float
    uploaded_at: datetime


class MatchResponse(BaseModel):
    job_description: str
    matches: List[MatchResult]
    total_candidates: int


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    database: str = "connected"
