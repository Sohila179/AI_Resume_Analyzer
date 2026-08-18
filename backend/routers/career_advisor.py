from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from rag.document_loader import load_documents
from rag.chunking import split_documents
from rag.embeddings import create_embeddings
from rag.vector_store import create_vector_store
from rag.career_advisor import CareerAdvisor

from database import SessionLocal
from models.resume import Resume
from models.analysis_resume import AnalysisResume
from routers.auth import get_current_user
from models.user import User

from services.skill_gap_analyzer import analyze_skill_gap


router = APIRouter(
    prefix="/career-advisor",
    tags=["Career Advisor"]
)


# ==========================================
# Request Schema
# ==========================================

class CareerQuestion(BaseModel):
    resume_id: int
    question: str


# ==========================================
# Database Dependency
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# Initialize RAG
# ==========================================

print("Initializing Career Advisor RAG...")

documents = load_documents()

print(f"Documents: {len(documents)}")

chunks = split_documents(documents)

print(f"Chunks: {len(chunks)}")

embeddings = create_embeddings(chunks)

print(f"Embeddings shape: {embeddings.shape}")

index = create_vector_store(
    chunks,
    embeddings
)

print("Career Advisor RAG initialized successfully.")


# ==========================================
# Create Career Advisor
# ==========================================

advisor = CareerAdvisor(
    chunks=chunks,
    index=index
)


# ==========================================
# Career Advisor Endpoint
# ==========================================

@router.post("/ask")
async def ask_career_advisor(
    data: CareerQuestion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------
    # 1. Get user's resume
    # --------------------------------------

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == data.resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )


    # --------------------------------------
    # 2. Get resume analysis
    # --------------------------------------

    analysis = (
        db.query(AnalysisResume)
        .filter(
            AnalysisResume.resume_id == resume.id
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=400,
            detail="Resume has not been analyzed yet"
        )


    # --------------------------------------
    # 3. User skills
    # --------------------------------------

    user_skills = analysis.skills


    # --------------------------------------
    # 4. Required AI Engineer skills
    # --------------------------------------

    required_skills = [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "SQL",
        "APIs",
        "Git",
        "TensorFlow",
        "PyTorch"
    ]


    # --------------------------------------
    # 5. Analyze skill gap
    # --------------------------------------

    skill_gap = analyze_skill_gap(
        user_skills=user_skills,
        required_skills=required_skills
    )


    # --------------------------------------
    # 6. Missing skills
    # --------------------------------------

    missing_skills = skill_gap["missing_skills"]

    matched_skills = skill_gap["matched_skills"]


    # --------------------------------------
    # 7. Build personalized question
    # --------------------------------------

    personalized_question = f"""
You are advising a user who wants to become an AI Engineer.

User's current skills:
{user_skills}

Skills already matched:
{matched_skills}

Skills missing from the AI Engineer requirements:
{missing_skills}

User's question:
{data.question}

Give personalized career advice based ONLY on the
provided knowledge base.

Explain:
1. Which skills the user already has.
2. Which skills are missing.
3. What the user should focus on next.

Do not invent information that is not supported
by the knowledge base.
"""


    # --------------------------------------
    # 8. Ask RAG Career Advisor
    # --------------------------------------

    result = advisor.ask(
        question=personalized_question,
        top_k=3
    )


    # --------------------------------------
    # 9. Return response
    # --------------------------------------

    return {
        "resume_id": resume.id,
        "question": data.question,
        "user_skills": user_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "answer": result["answer"]
    }
# ==========================================
# Personalized Learning Roadmap
# ==========================================

@router.post("/roadmap")
async def generate_roadmap(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------
    # 1. Get user's resume
    # --------------------------------------

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
            status_code=404,
            detail="Resume not found"
        )


    # --------------------------------------
    # 2. Get resume analysis
    # --------------------------------------

    analysis = (
        db.query(AnalysisResume)
        .filter(
            AnalysisResume.resume_id == resume.id
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=400,
            detail="Resume has not been analyzed yet"
        )


    # --------------------------------------
    # 3. User skills
    # --------------------------------------

    user_skills = analysis.skills


    # --------------------------------------
    # 4. AI Engineer required skills
    # --------------------------------------

    required_skills = [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "SQL",
        "APIs",
        "Git",
        "TensorFlow",
        "PyTorch"
    ]


    # --------------------------------------
    # 5. Calculate skill gap
    # --------------------------------------

    skill_gap = analyze_skill_gap(
        user_skills=user_skills,
        required_skills=required_skills
    )


    missing_skills = skill_gap["missing_skills"]


    # --------------------------------------
    # 6. Check if there are missing skills
    # --------------------------------------

    if not missing_skills:

        return {
            "resume_id": resume.id,
            "message": "You already have all the required skills for this AI Engineer roadmap.",
            "missing_skills": [],
            "roadmap": []
        }


    # --------------------------------------
    # 7. Build roadmap question
    # --------------------------------------

    roadmap_question = f"""
You are a Career Advisor helping a user become an AI Engineer.

The user's current skills are:

{user_skills}

The user's missing skills are:

{missing_skills}

Create a personalized learning roadmap for ONLY the missing skills.

Use ONLY the provided knowledge base.

For each missing skill:

1. Explain what the skill is.
2. Explain the topics the user should learn.
3. Put the skills in a logical learning order.
4. Suggest practical projects if they are mentioned in the knowledge base.

Do not recommend skills that are not missing.

Do not invent information that is not available
in the knowledge base.

Return a clear and structured learning roadmap.
"""


    # --------------------------------------
    # 8. Generate roadmap using RAG
    # --------------------------------------

    result = advisor.ask(
        question=roadmap_question,
        top_k=5
    )


    # --------------------------------------
    # 9. Return roadmap
    # --------------------------------------

    return {
        "resume_id": resume.id,
        "missing_skills": missing_skills,
        "roadmap": result["answer"]
    }