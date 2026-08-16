from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import SessionLocal
from models.user import User
from models.job import Job
from schemas.job import JobCreate, JobUpdate, JobResponse
from routers.auth import get_current_user


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create jobs"
        )

    new_job = Job(
        employer_id=current_user.id,
        title=job.title,
        content=job.content,
        required_skills=job.required_skills
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get(
    "/",
    response_model=list[JobResponse]
)
def get_jobs(
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).all()
    return jobs

@router.get(
    "/search",
    response_model=list[JobResponse]
)
def search_jobs(
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).all()

    if not keyword:
        return jobs

    keyword = keyword.lower()

    results = []

    for job in jobs:
        title_match = keyword in job.title.lower()
        content_match = keyword in job.content.lower()

        skills_match = any(
            keyword in skill.lower()
            for skill in job.required_skills
        )

        if title_match or content_match or skills_match:
            results.append(job)

    return results

@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job


@router.put(
    "/{job_id}",
    response_model=JobResponse
)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can update jobs"
        )

    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own jobs"
        )

    if job_data.title is not None:
        job.title = job_data.title

    if job_data.content is not None:
        job.content = job_data.content

    if job_data.required_skills is not None:
        job.required_skills = job_data.required_skills

    db.commit()
    db.refresh(job)

    return job


@router.delete(
    "/{job_id}"
)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can delete jobs"
        )

    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own jobs"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully"
    }