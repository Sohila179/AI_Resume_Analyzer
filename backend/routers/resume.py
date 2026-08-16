from fastapi import (APIRouter,status,HTTPException,
                     Response,Path,Query,Header,Body,Request ,UploadFile,Form,File,Depends, Cookie)

from config import Settings
from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Annotated
from routers.auth import get_current_user
from models.user import User
from uuid import uuid4
from pathlib import Path
import shutil
from models.resume import Resume
from schemas.resume import ResumeResponse
from services.resume_parser import extract_text_from_pdf
from services.resume_analyzer import analyze_resume
from models.analysis_resume import AnalysisResume
settings=Settings()

resume_router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy=Annotated[Session,Depends(get_db)]  

@resume_router.post("/upload",status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_extensions = [".pdf", ".docx"]

    extension = Path(file.filename).suffix.lower()


    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
   
    unique_filename = f"{uuid4()}{extension}"

    file_path = upload_dir / unique_filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_resume = Resume(
        resume_file=str(file_path),
        user_id=current_user.id
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return new_resume
    
    
@resume_router.get("/", response_model=list[ResumeResponse])
def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .all()
    )

    return resumes


     

@resume_router.post("/{resume_id}/analyze")
def analyze_resume_endpoint(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Extract text from PDF
    text = extract_text_from_pdf(resume.resume_file)

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from resume"
        )

    # Analyze using Hugging Face
    analysis = analyze_resume(text)

    # Check if this resume was analyzed before
    existing_analysis = (
        db.query(AnalysisResume)
        .filter(AnalysisResume.resume_id == resume.id)
        .first()
    )

    if existing_analysis:
        existing_analysis.skills = analysis["skills"]
        existing_analysis.experience = analysis["experience"]
        existing_analysis.education = analysis["education"]
        existing_analysis.summary = analysis["summary"]

        db.commit()
        db.refresh(existing_analysis)

        saved_analysis = existing_analysis

    else:
        saved_analysis = AnalysisResume(
            skills=analysis["skills"],
            experience=analysis["experience"],
            education=analysis["education"],
            summary=analysis["summary"],
            resume_id=resume.id
        )

        db.add(saved_analysis)
        db.commit()
        db.refresh(saved_analysis)

    return saved_analysis
    