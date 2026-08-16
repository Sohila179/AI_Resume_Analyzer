from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User
from models.resume import Resume
from models.job import Job
from models.recommendation import Recommendation
from routers.auth import get_current_user
from services.job_matching import calculate_match


router = APIRouter(
    prefix="/job-matching",
    tags=["Job Matching"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/resume/{resume_id}")
def match_resume_with_jobs(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    analysis = (
        resume.resume_analysis
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume must be analyzed first"
        )

    resume_skills = analysis.skills or []

    jobs = db.query(Job).all()

    if not jobs:
        return {
            "resume_id": resume_id,
            "message": "No jobs available",
            "recommendations": []
        }

    recommendations = []

    for job in jobs:

        result = calculate_match(
            resume_skills=resume_skills,
            required_skills=job.required_skills or []
        )

        recommendation = Recommendation(
            resume_id=resume.id,
            job_id=job.id,
            score=result["score"],
            reason=(
                f"Matched {len(result['matched_skills'])} "
                f"out of {len(job.required_skills or [])} required skills"
            ),
            matched_skills=result["matched_skills"],
            missing_skills=result["missing_skills"]
        )

        db.add(recommendation)

        recommendations.append({
            "job_id": job.id,
            "title": job.title,
            "score": result["score"],
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "reason": recommendation.reason
        })

    db.commit()

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "resume_id": resume_id,
        "recommendations": recommendations
    }