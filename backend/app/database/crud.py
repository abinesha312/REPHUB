# backend/app/database/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
import bcrypt
from datetime import datetime

from .models import User, Resume, JobDescription, Match

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str):
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    db_user = User(
        username=username,
        email=email,
        password_hash=hashed_password.decode('utf-8')
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_latest_resume_version(db: Session, user_id: int):
    # Get the latest version number for a user's resumes
    result = db.query(Resume).filter(Resume.user_id == user_id).order_by(desc(Resume.version)).first()
    if result:
        return result.version
    return None

def create_resume(db: Session, user_id: int, version: int, file_path: str, parsed_data: dict):
    db_resume = Resume(
        user_id=user_id,
        version=version,
        file_path=file_path,
        parsed_data=parsed_data,
        upload_date=datetime.now()
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def create_job_description(db: Session, user_id: int, title: str, company: str, url: str, description: str, parsed_data: dict):
    db_jd = JobDescription(
        user_id=user_id,
        title=title,
        company=company,
        url=url,
        description=description,
        parsed_data=parsed_data,
        upload_date=datetime.now()
    )
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd

def create_match(db: Session, resume_id: int, job_id: int, match_score: float):
    db_match = Match(
        resume_id=resume_id,
        job_id=job_id,
        match_score=match_score,
        match_date=datetime.now()
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_all_user_resumes(db: Session, user_id: int):
    return db.query(Resume).filter(Resume.user_id == user_id).all()

def get_all_user_job_descriptions(db: Session, user_id: int):
    return db.query(JobDescription).filter(JobDescription.user_id == user_id).all()

def get_resume(db: Session, resume_id: int):
    return db.query(Resume).filter(Resume.id == resume_id).first()

def get_job_description(db: Session, job_id: int):
    return db.query(JobDescription).filter(JobDescription.id == job_id).first()

def get_all_matches(db: Session):
    return db.query(Match).all()

def get_match(db: Session, match_id: int):
    return db.query(Match).filter(Match.id == match_id).first()
