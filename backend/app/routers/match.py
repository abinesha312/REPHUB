"""Job description matching router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging

from ..database import get_db
from ..models import Resume
from ..schemas import MatchRequest, MatchResponse, MatchResult
from ..embeddings import get_embedding_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/match", tags=["match"])


@router.post("/", response_model=MatchResponse)
async def match_job_description(
    request: MatchRequest,
    db: Session = Depends(get_db)
):
    """
    Match resumes to a job description using vector similarity.
    
    Args:
        request: Match request with job description
        db: Database session
    
    Returns:
        Ranked list of matching resumes with similarity scores
    """
    # Generate embedding for job description
    embedding_service = get_embedding_service()
    
    try:
        jd_embedding = embedding_service.embed_text(request.job_description)
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process job description: {str(e)}"
        )
    
    # Build query with filters
    base_query = db.query(Resume).filter(Resume.embedding.isnot(None))
    
    if request.user_id:
        base_query = base_query.filter(Resume.user_id == request.user_id)
    
    # Get total candidates
    total_candidates = base_query.count()
    
    if total_candidates == 0:
        return MatchResponse(
            job_description=request.job_description,
            matches=[],
            total_candidates=0
        )
    
    # Perform vector similarity search using pgvector
    # Using cosine distance: 1 - (embedding <=> jd_embedding)
    # Note: pgvector's <=> operator returns cosine distance (0 = identical, 2 = opposite)
    # We convert to similarity: similarity = 1 - (distance / 2)
    
    embedding_str = "[" + ",".join(map(str, jd_embedding)) + "]"
    
    sql = text("""
        SELECT 
            id,
            user_id,
            format,
            version,
            filename,
            uploaded_at,
            1 - (embedding <=> :embedding::vector) as similarity
        FROM resumes
        WHERE embedding IS NOT NULL
        """ + (f" AND user_id = :user_id" if request.user_id else "") + """
        ORDER BY embedding <=> :embedding::vector
        LIMIT :limit
    """)
    
    params = {
        "embedding": embedding_str,
        "limit": request.limit
    }
    if request.user_id:
        params["user_id"] = request.user_id
    
    try:
        results = db.execute(sql, params).fetchall()
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
    
    # Build response
    matches = []
    for row in results:
        matches.append(MatchResult(
            resume_id=row.id,
            user_id=row.user_id,
            format=row.format,
            version=row.version,
            filename=row.filename,
            similarity_score=float(row.similarity),
            uploaded_at=row.uploaded_at
        ))
    
    return MatchResponse(
        job_description=request.job_description,
        matches=matches,
        total_candidates=total_candidates
    )
