"""Resume management router."""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pathlib import Path
from typing import Optional
import logging

from ..database import get_db
from ..models import Resume, User
from ..schemas import ResumeResponse, ResumeListResponse
from ..storage import get_storage_backend
from ..extractors import TextExtractor
from ..embeddings import get_embedding_service
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resumes", tags=["resumes"])

settings = get_settings()
storage = get_storage_backend(settings.storage_root)
extractor = TextExtractor()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    format: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new resume version.
    
    Args:
        file: Resume file (PDF, LaTeX, DOCX, etc.)
        user_id: User ID
        format: Format type (pdf, latex, doc, docx)
        db: Database session
    """
    # Validate format
    format = format.lower()
    allowed_formats = ["pdf", "latex", "doc", "docx", "tex"]
    if format not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Allowed: {', '.join(allowed_formats)}"
        )
    
    # Ensure user exists (create default user if needed)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username=f"user_{user_id}")
        db.add(user)
        db.commit()
    
    # Get latest version for this user+format
    latest = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.format == format
    ).order_by(desc(Resume.version)).first()
    
    next_version = (latest.version + 1) if latest else 1
    
    # Build storage path: {user_id}/{format}/v_{N}/{filename}
    storage_path = f"{user_id}/{format}/v_{next_version}/{file.filename}"
    
    try:
        # Save file to storage
        file_content = await file.read()
        await file.seek(0)  # Reset for potential re-read
        
        # Save using storage backend
        import io
        storage.save(io.BytesIO(file_content), storage_path)
        
        # Get full path for text extraction
        full_path = storage.get_full_path(storage_path)
        
        # Extract text
        try:
            extracted_text = extractor.extract(str(full_path), format)
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
            extracted_text = ""
        
        # Generate embedding
        embedding_service = get_embedding_service()
        try:
            embedding = embedding_service.embed_text(extracted_text) if extracted_text else None
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            embedding = None
        
        # Create database record
        resume = Resume(
            user_id=user_id,
            format=format,
            version=next_version,
            filename=file.filename,
            storage_path=storage_path,
            content_type=file.content_type,
            file_size=len(file_content),
            extracted_text=extracted_text,
            embedding=embedding
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return ResumeResponse.from_orm_with_embedding(resume)
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        # Cleanup on failure
        try:
            storage.delete(storage_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list", response_model=ResumeListResponse)
async def list_resumes(
    user_id: Optional[int] = Query(None),
    format: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List resumes with optional filtering.
    
    Args:
        user_id: Filter by user ID
        format: Filter by format
        db: Database session
    """
    query = db.query(Resume)
    
    if user_id:
        query = query.filter(Resume.user_id == user_id)
    if format:
        query = query.filter(Resume.format == format.lower())
    
    resumes = query.order_by(
        Resume.user_id,
        Resume.format,
        desc(Resume.version)
    ).all()
    
    return ResumeListResponse(
        resumes=[ResumeResponse.from_orm_with_embedding(r) for r in resumes],
        total=len(resumes)
    )


@router.get("/download/{resume_id}")
async def download_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Download a resume file.
    
    Args:
        resume_id: Resume ID
        db: Database session
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    full_path = storage.get_full_path(resume.storage_path)
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found on storage")
    
    return FileResponse(
        path=str(full_path),
        filename=resume.filename,
        media_type=resume.content_type or "application/octet-stream"
    )


@router.get("/folders", response_model=dict)
async def list_folders(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get folder structure (formats and versions).
    
    Returns a tree of user → format → versions.
    """
    query = db.query(Resume)
    if user_id:
        query = query.filter(Resume.user_id == user_id)
    
    resumes = query.order_by(Resume.user_id, Resume.format, Resume.version).all()
    
    # Build tree structure
    tree = {}
    for resume in resumes:
        uid = resume.user_id
        fmt = resume.format
        
        if uid not in tree:
            tree[uid] = {}
        if fmt not in tree[uid]:
            tree[uid][fmt] = []
        
        tree[uid][fmt].append({
            "version": resume.version,
            "resume_id": resume.id,
            "filename": resume.filename,
            "uploaded_at": resume.uploaded_at.isoformat()
        })
    
    return {"folders": tree}
