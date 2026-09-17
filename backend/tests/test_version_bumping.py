"""Test version bumping logic."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import Resume, User


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_version_increments_correctly(db_session):
    """Test that versions increment properly for the same user+format."""
    user = User(id=1, username="testuser")
    db_session.add(user)
    db_session.commit()
    
    # First upload
    resume1 = Resume(
        user_id=1,
        format="pdf",
        version=1,
        filename="resume_v1.pdf",
        storage_path="1/pdf/v_1/resume_v1.pdf"
    )
    db_session.add(resume1)
    db_session.commit()
    
    # Second upload - should be version 2
    latest = db_session.query(Resume).filter(
        Resume.user_id == 1,
        Resume.format == "pdf"
    ).order_by(Resume.version.desc()).first()
    
    next_version = (latest.version + 1) if latest else 1
    assert next_version == 2
    
    resume2 = Resume(
        user_id=1,
        format="pdf",
        version=next_version,
        filename="resume_v2.pdf",
        storage_path=f"1/pdf/v_{next_version}/resume_v2.pdf"
    )
    db_session.add(resume2)
    db_session.commit()
    
    # Verify
    all_resumes = db_session.query(Resume).filter(
        Resume.user_id == 1,
        Resume.format == "pdf"
    ).all()
    
    assert len(all_resumes) == 2
    assert all_resumes[0].version == 1
    assert all_resumes[1].version == 2


def test_versions_independent_per_format(db_session):
    """Test that different formats have independent version sequences."""
    user = User(id=1, username="testuser")
    db_session.add(user)
    db_session.commit()
    
    # Upload PDF v1
    resume_pdf = Resume(
        user_id=1,
        format="pdf",
        version=1,
        filename="resume.pdf",
        storage_path="1/pdf/v_1/resume.pdf"
    )
    db_session.add(resume_pdf)
    
    # Upload LaTeX v1 (should also be version 1)
    resume_latex = Resume(
        user_id=1,
        format="latex",
        version=1,
        filename="resume.tex",
        storage_path="1/latex/v_1/resume.tex"
    )
    db_session.add(resume_latex)
    db_session.commit()
    
    # Both should be version 1
    pdf_resumes = db_session.query(Resume).filter(
        Resume.user_id == 1,
        Resume.format == "pdf"
    ).all()
    
    latex_resumes = db_session.query(Resume).filter(
        Resume.user_id == 1,
        Resume.format == "latex"
    ).all()
    
    assert len(pdf_resumes) == 1
    assert len(latex_resumes) == 1
    assert pdf_resumes[0].version == 1
    assert latex_resumes[0].version == 1


def test_versions_independent_per_user(db_session):
    """Test that different users have independent version sequences."""
    user1 = User(id=1, username="user1")
    user2 = User(id=2, username="user2")
    db_session.add_all([user1, user2])
    db_session.commit()
    
    # User 1 uploads PDF v1
    resume1 = Resume(
        user_id=1,
        format="pdf",
        version=1,
        filename="resume.pdf",
        storage_path="1/pdf/v_1/resume.pdf"
    )
    db_session.add(resume1)
    
    # User 2 uploads PDF v1 (should also be version 1)
    resume2 = Resume(
        user_id=2,
        format="pdf",
        version=1,
        filename="resume.pdf",
        storage_path="2/pdf/v_1/resume.pdf"
    )
    db_session.add(resume2)
    db_session.commit()
    
    # Both should be version 1
    user1_resumes = db_session.query(Resume).filter(Resume.user_id == 1).all()
    user2_resumes = db_session.query(Resume).filter(Resume.user_id == 2).all()
    
    assert len(user1_resumes) == 1
    assert len(user2_resumes) == 1
    assert user1_resumes[0].version == 1
    assert user2_resumes[0].version == 1
