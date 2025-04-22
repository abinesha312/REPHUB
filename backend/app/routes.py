# backend/app/api/routes.py
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
from datetime import datetime

from ..database.database import get_db
from ..database import crud
from ..services.resume_parser import ResumeParser
from ..services.jd_analyzer import JobDescriptionAnalyzer
from ..services.matcher import ResumeMatcher

router = APIRouter()
resume_parser = ResumeParser()
jd_analyzer = JobDescriptionAnalyzer()
resume_matcher = ResumeMatcher()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/users/")
def create_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, username, email, password)

@router.post("/upload-resume/")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Validate user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Parse resume
    try:
        parsed_data = resume_parser.parse_resume(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")
    
    # Determine version number
    latest_version = crud.get_latest_resume_version(db, user_id)
    new_version = latest_version + 1 if latest_version else 1
    
    # Save resume to database
    resume = crud.create_resume(
        db, 
        user_id=user_id, 
        version=new_version, 
        file_path=file_path, 
        parsed_data=parsed_data
    )
    
    return {
        "id": resume.id,
        "version": resume.version,
        "upload_date": resume.upload_date,
        "parsed_data": parsed_data
    }

@router.post("/upload-job-description/")
async def upload_job_description(
    user_id: int = Form(...),
    title: str = Form(...),
    company: str = Form(...),
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Validate user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not file and not url:
        raise HTTPException(status_code=400, detail="Either file or URL must be provided")
    
    # Process job description
    try:
        if file:
            # Save file
            file_path = os.path.join(UPLOAD_DIR, f"jd_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            analysis = jd_analyzer.analyze_job_description(file_path, is_url=False)
            description = analysis["full_text"]
        else:
            analysis = jd_analyzer.analyze_job_description(url, is_url=True)
            description = analysis["full_text"]
            file_path = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing job description: {str(e)}")
    
    # Save job description to database
    jd = crud.create_job_description(
        db, 
        user_id=user_id, 
        title=title, 
        company=company, 
        url=url if url else None, 
        description=description, 
        parsed_data=analysis
    )
    
    return {
        "id": jd.id,
        "title": jd.title,
        "company": jd.company,
        "upload_date": jd.upload_date,
        "analysis": analysis
    }

@router.get("/match-resumes/{job_id}")
def match_resumes(
    job_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Get job description
    job = crud.get_job_description(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Get all resumes for the user
    resumes = crud.get_all_user_resumes(db, user_id)
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for user")
    
    # Match resumes against job description
    matched_resumes = resume_matcher.rank_resumes(resumes, job.parsed_data)
    
    # Get top 5 matches
    top_matches = matched_resumes[:5]
    
    # Save matches to database
    for match in top_matches:
        crud.create_match(
            db,
            resume_id=match["resume_id"],
            job_id=job_id,
            match_score=match["overall_score"]
        )
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "company": job.company,
        "matched_resumes": top_matches
    }

@router.get("/resumes/{user_id}")
def get_user_resumes(
    user_id: int,
    db: Session = Depends(get_db)
):
    resumes = crud.get_all_user_resumes(db, user_id)
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for user")
    
    return resumes

@router.get("/job-descriptions/{user_id}")
def get_user_job_descriptions(
    user_id: int,
    db: Session = Depends(get_db)
):
    jds = crud.get_all_user_job_descriptions(db, user_id)
    if not jds:
        raise HTTPException(status_code=404, detail="No job descriptions found for user")
    
    return jds
