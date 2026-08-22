# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.orm import Session

# from rag.document_loader import load_documents
# from rag.chunking import split_documents
# from rag.embeddings import create_embeddings
# from rag.vector_store import create_vector_store
# from rag.career_advisor import CareerAdvisor

# from database import SessionLocal
# from models.resume import Resume
# from models.analysis_resume import AnalysisResume
# from routers.auth import get_current_user
# from models.user import User

# from services.skill_gap_analyzer import analyze_skill_gap


# router = APIRouter(
#     prefix="/career-advisor",
#     tags=["Career Advisor"]
# )


# # ==========================================
# # Request Schema
# # ==========================================

# class CareerQuestion(BaseModel):
#     resume_id: int
#     question: str


# # ==========================================
# # Database Dependency
# # ==========================================

# def get_db():
#     db = SessionLocal()

#     try:
#         yield db
#     finally:
#         db.close()


# # ==========================================
# # Initialize RAG
# # ==========================================

# print("Initializing Career Advisor RAG...")

# documents = load_documents()

# print(f"Documents: {len(documents)}")

# chunks = split_documents(documents)

# print(f"Chunks: {len(chunks)}")

# embeddings = create_embeddings(chunks)

# print(f"Embeddings shape: {embeddings.shape}")

# index = create_vector_store(
#     chunks,
#     embeddings
# )

# print("Career Advisor RAG initialized successfully.")


# # ==========================================
# # Create Career Advisor
# # ==========================================

# advisor = CareerAdvisor(
#     chunks=chunks,
#     index=index
# )


# # ==========================================
# # Career Advisor Endpoint
# # ==========================================

# @router.post("/ask")
# async def ask_career_advisor(
#     data: CareerQuestion,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):

#     # --------------------------------------
#     # 1. Get user's resume
#     # --------------------------------------

#     resume = (
#         db.query(Resume)
#         .filter(
#             Resume.id == data.resume_id,
#             Resume.user_id == current_user.id
#         )
#         .first()
#     )

#     if not resume:
#         raise HTTPException(
#             status_code=404,
#             detail="Resume not found"
#         )


#     # --------------------------------------
#     # 2. Get resume analysis
#     # --------------------------------------

#     analysis = (
#         db.query(AnalysisResume)
#         .filter(
#             AnalysisResume.resume_id == resume.id
#         )
#         .first()
#     )

#     if not analysis:
#         raise HTTPException(
#             status_code=400,
#             detail="Resume has not been analyzed yet"
#         )


#     # --------------------------------------
#     # 3. User skills
#     # --------------------------------------

#     user_skills = analysis.skills


#     # --------------------------------------
#     # 4. Required AI Engineer skills
#     # --------------------------------------

#     required_skills = [
#         "Python",
#         "Machine Learning",
#         "Deep Learning",
#         "SQL",
#         "APIs",
#         "Git",
#         "TensorFlow",
#         "PyTorch"
#     ]


#     # --------------------------------------
#     # 5. Analyze skill gap
#     # --------------------------------------

#     skill_gap = analyze_skill_gap(
#         user_skills=user_skills,
#         required_skills=required_skills
#     )


#     # --------------------------------------
#     # 6. Missing skills
#     # --------------------------------------

#     missing_skills = skill_gap["missing_skills"]

#     matched_skills = skill_gap["matched_skills"]


#     # --------------------------------------
#     # 7. Build personalized question
#     # --------------------------------------

#     personalized_question = f"""
# You are advising a user who wants to become an AI Engineer.

# User's current skills:
# {user_skills}

# Skills already matched:
# {matched_skills}

# Skills missing from the AI Engineer requirements:
# {missing_skills}

# User's question:
# {data.question}

# Give personalized career advice based ONLY on the
# provided knowledge base.

# Explain:
# 1. Which skills the user already has.
# 2. Which skills are missing.
# 3. What the user should focus on next.

# Do not invent information that is not supported
# by the knowledge base.
# """


#     # --------------------------------------
#     # 8. Ask RAG Career Advisor
#     # --------------------------------------

#     result = advisor.ask(
#         question=personalized_question,
#         top_k=3
#     )


#     # --------------------------------------
#     # 9. Return response
#     # --------------------------------------

#     return {
#         "resume_id": resume.id,
#         "question": data.question,
#         "user_skills": user_skills,
#         "matched_skills": matched_skills,
#         "missing_skills": missing_skills,
#         "answer": result["answer"]
#     }
# # ==========================================
# # Personalized Learning Roadmap
# # ==========================================

# @router.post("/roadmap")
# async def generate_roadmap(
#     resume_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):

#     # --------------------------------------
#     # 1. Get user's resume
#     # --------------------------------------

#     resume = (
#         db.query(Resume)
#         .filter(
#             Resume.id == resume_id,
#             Resume.user_id == current_user.id
#         )
#         .first()
#     )

#     if not resume:
#         raise HTTPException(
#             status_code=404,
#             detail="Resume not found"
#         )


#     # --------------------------------------
#     # 2. Get resume analysis
#     # --------------------------------------

#     analysis = (
#         db.query(AnalysisResume)
#         .filter(
#             AnalysisResume.resume_id == resume.id
#         )
#         .first()
#     )

#     if not analysis:
#         raise HTTPException(
#             status_code=400,
#             detail="Resume has not been analyzed yet"
#         )


#     # --------------------------------------
#     # 3. User skills
#     # --------------------------------------

#     user_skills = analysis.skills


#     # --------------------------------------
#     # 4. AI Engineer required skills
#     # --------------------------------------

#     required_skills = [
#         "Python",
#         "Machine Learning",
#         "Deep Learning",
#         "SQL",
#         "APIs",
#         "Git",
#         "TensorFlow",
#         "PyTorch"
#     ]


#     # --------------------------------------
#     # 5. Calculate skill gap
#     # --------------------------------------

#     skill_gap = analyze_skill_gap(
#         user_skills=user_skills,
#         required_skills=required_skills
#     )


#     missing_skills = skill_gap["missing_skills"]


#     # --------------------------------------
#     # 6. Check if there are missing skills
#     # --------------------------------------

#     if not missing_skills:

#         return {
#             "resume_id": resume.id,
#             "message": "You already have all the required skills for this AI Engineer roadmap.",
#             "missing_skills": [],
#             "roadmap": []
#         }


#     # --------------------------------------
#     # 7. Build roadmap question
#     # --------------------------------------

#     roadmap_question = f"""
# You are a Career Advisor helping a user become an AI Engineer.

# The user's current skills are:

# {user_skills}

# The user's missing skills are:

# {missing_skills}

# Create a personalized learning roadmap for ONLY the missing skills.

# Use ONLY the provided knowledge base.

# For each missing skill:

# 1. Explain what the skill is.
# 2. Explain the topics the user should learn.
# 3. Put the skills in a logical learning order.
# 4. Suggest practical projects if they are mentioned in the knowledge base.

# Do not recommend skills that are not missing.

# Do not invent information that is not available
# in the knowledge base.

# Return a clear and structured learning roadmap.
# """


#     # --------------------------------------
#     # 8. Generate roadmap using RAG
#     # --------------------------------------

#     result = advisor.ask(
#         question=roadmap_question,
#         top_k=5
#     )


#     # --------------------------------------
#     # 9. Return roadmap
#     # --------------------------------------

#     return {
#         "resume_id": resume.id,
#         "missing_skills": missing_skills,
#         "roadmap": result["answer"]
#     }



from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import re

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


# =========================================================
# REQUEST SCHEMA
# =========================================================

class CareerQuestion(BaseModel):
    resume_id: int
    question: str


# =========================================================
# DATABASE
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# INITIALIZE RAG
# =========================================================

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


advisor = CareerAdvisor(
    chunks=chunks,
    index=index
)


# =========================================================
# AI ENGINEER SKILLS
# =========================================================

REQUIRED_SKILLS = [
    "Python",
    "Machine Learning",
    "Deep Learning",
    "SQL",
    "APIs",
    "Git",
    "TensorFlow",
    "PyTorch"
]


# =========================================================
# HELPER: GET RESUME + ANALYSIS
# =========================================================

def get_resume_analysis(
    resume_id: int,
    db: Session,
    current_user: User
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
            status_code=404,
            detail="Resume not found"
        )

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

    return resume, analysis


# =========================================================
# CAREER ADVISOR
# =========================================================

@router.post("/ask")
async def ask_career_advisor(
    data: CareerQuestion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    resume, analysis = get_resume_analysis(
        data.resume_id,
        db,
        current_user
    )

    user_skills = analysis.skills or []

    skill_gap = analyze_skill_gap(
        user_skills=user_skills,
        required_skills=REQUIRED_SKILLS
    )

    missing_skills = skill_gap["missing_skills"]

    matched_skills = skill_gap["matched_skills"]

    personalized_question = f"""
You are advising a user who wants to become an AI Engineer.

Current user skills:
{user_skills}

Matched skills:
{matched_skills}

Missing skills:
{missing_skills}

User question:
{data.question}

Use ONLY the provided knowledge base.

Explain:

1. Skills the user already has.
2. Skills that are missing.
3. What the user should focus on next.

Do not invent information.
"""

    result = advisor.ask(
        question=personalized_question,
        top_k=3
    )

    return {
        "resume_id": resume.id,
        "question": data.question,
        "user_skills": user_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "answer": result["answer"]
    }


# =========================================================
# EXTRACT JSON FROM AI RESPONSE
# =========================================================

def extract_json(text):

    if not text:
        return None

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*$",
        "",
        text
    )

    # Try direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # Find first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)
        except Exception:
            pass

    return None


# =========================================================
# NORMALIZE ROADMAP
# =========================================================

def normalize_roadmap(
    data,
    missing_skills
):

    if not isinstance(data, dict):
        data = {}

    raw_steps = data.get("steps", [])

    if not isinstance(raw_steps, list):
        raw_steps = []

    steps = []

    for index, step in enumerate(raw_steps):

        if not isinstance(step, dict):
            continue

        title = str(
            step.get(
                "title",
                f"Learning Stage {index + 1}"
            )
        ).strip()

        skill = str(
            step.get(
                "skill",
                title
            )
        ).strip()

        description = str(
            step.get(
                "description",
                ""
            )
        ).strip()

        topics = step.get(
            "topics",
            []
        )

        if not isinstance(topics, list):
            topics = [str(topics)]

        topics = [
            str(topic).strip()
            for topic in topics
            if str(topic).strip()
        ]

        projects = step.get(
            "projects",
            []
        )

        if not isinstance(projects, list):
            projects = [str(projects)]

        projects = [
            str(project).strip()
            for project in projects
            if str(project).strip()
        ]

        resources = step.get(
            "resources",
            []
        )

        if not isinstance(resources, list):
            resources = [str(resources)]

        resources = [
            str(resource).strip()
            for resource in resources
            if str(resource).strip()
        ]

        duration = str(
            step.get(
                "duration",
                ""
            )
        ).strip()

        level = str(
            step.get(
                "level",
                "Learning"
            )
        ).strip()

        steps.append({
            "step": len(steps) + 1,
            "title": title,
            "skill": skill,
            "description": description,
            "topics": topics,
            "projects": projects,
            "resources": resources,
            "duration": duration,
            "level": level
        })

    return {
        "title": data.get(
            "title",
            "Your AI Engineer Learning Path"
        ),

        "goal": data.get(
            "goal",
            "Build the missing skills needed for an AI Engineer role."
        ),

        "steps": steps,

        "missing_skills": missing_skills,

        "total_steps": len(steps)
    }


# =========================================================
# PERSONALIZED LEARNING ROADMAP
# =========================================================

@router.post("/roadmap")
async def generate_roadmap(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # 1. Resume + Analysis
    # -----------------------------------------------------

    resume, analysis = get_resume_analysis(
        resume_id,
        db,
        current_user
    )

    # -----------------------------------------------------
    # 2. User skills
    # -----------------------------------------------------

    user_skills = analysis.skills or []

    # -----------------------------------------------------
    # 3. Skill gap
    # -----------------------------------------------------

    skill_gap = analyze_skill_gap(
        user_skills=user_skills,
        required_skills=REQUIRED_SKILLS
    )

    missing_skills = skill_gap["missing_skills"]

    matched_skills = skill_gap["matched_skills"]

    # -----------------------------------------------------
    # 4. No missing skills
    # -----------------------------------------------------

    if not missing_skills:

        return {
            "resume_id": resume.id,

            "title":
                "AI Engineer Career Path",

            "goal":
                "You already have the required skills.",

            "missing_skills": [],

            "matched_skills":
                matched_skills,

            "steps": [],

            "total_steps": 0,

            "message":
                "You already have all the required skills."
        }

    # -----------------------------------------------------
    # 5. Structured AI Prompt
    # -----------------------------------------------------

    roadmap_question = f"""
You are an expert Career Roadmap Generator.

The user's target career is:

AI Engineer

The user's current skills are:

{user_skills}

The user's missing skills are:

{missing_skills}

Create a personalized learning roadmap ONLY for the
missing skills.

IMPORTANT:

Use ONLY information supported by the knowledge base.

Do not invent courses, websites, certifications,
technologies, or projects that are not present
in the knowledge base.

Create a logical learning sequence from foundation
to advanced level.

Return ONLY valid JSON.

Do not use markdown.

Do not write explanations outside the JSON.

Use exactly this structure:

{{
  "title": "Your AI Engineer Learning Path",
  "goal": "Short description of the final career goal",
  "steps": [
    {{
      "title": "Step title",
      "skill": "One missing skill",
      "description": "Short explanation",
      "topics": [
        "Topic 1",
        "Topic 2"
      ],
      "projects": [
        "Practical project if supported by knowledge base"
      ],
      "resources": [
        "Learning resource if supported by knowledge base"
      ],
      "duration": "Suggested duration",
      "level": "Foundation"
    }}
  ]
}}

Rules:

1. Every step must focus on a missing skill.
2. Do not add skills that are already matched.
3. Order the steps logically.
4. Start with foundation skills.
5. Continue toward advanced skills.
6. Include projects only when supported by the knowledge base.
7. Include resources only when supported by the knowledge base.
8. Keep the roadmap practical.
9. Return valid JSON only.

Missing skills:
{missing_skills}
"""

    # -----------------------------------------------------
    # 6. Generate AI roadmap
    # -----------------------------------------------------

    result = advisor.ask(
        question=roadmap_question,
        top_k=5
    )

    raw_answer = result.get(
        "answer",
        ""
    )

    # -----------------------------------------------------
    # 7. Parse JSON
    # -----------------------------------------------------

    roadmap_data = extract_json(
        raw_answer
    )

    # -----------------------------------------------------
    # 8. Fallback if AI doesn't return JSON
    # -----------------------------------------------------

    if roadmap_data is None:

        roadmap_data = {
            "title":
                "Your AI Engineer Learning Path",

            "goal":
                "Build the missing skills required for an AI Engineer role.",

            "steps": []
        }

        for index, skill in enumerate(
            missing_skills
        ):

            roadmap_data["steps"].append({

                "title":
                    f"Learn {skill}",

                "skill":
                    skill,

                "description":
                    f"Build practical knowledge in {skill}.",

                "topics": [],

                "projects": [],

                "resources": [],

                "duration":
                    "",

                "level":
                    "Foundation"
                    if index == 0
                    else "Intermediate"
            })

    # -----------------------------------------------------
    # 9. Normalize
    # -----------------------------------------------------

    roadmap = normalize_roadmap(
        roadmap_data,
        missing_skills
    )

    # -----------------------------------------------------
    # 10. Final Response
    # -----------------------------------------------------

    return {
        "resume_id":
            resume.id,

        "title":
            roadmap["title"],

        "goal":
            roadmap["goal"],

        "missing_skills":
            missing_skills,

        "matched_skills":
            matched_skills,

        "steps":
            roadmap["steps"],

        "total_steps":
            roadmap["total_steps"]
    }