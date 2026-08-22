from fastapi import FastAPI
from config import Settings
from database import Base,engine
from models.user import User
from models.resume import Resume
from models.analysis_resume import AnalysisResume
from models.recommendation import Recommendation
from models.career_advisor import CareerAdvisor
from models.job import Job 
from routers import jobs
from routers import auth
from routers import job_matching
from routers.resume import resume_router
from routers import career_advisor
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)
settings = Settings()

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    url=settings.DATABASE_URL
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume_router)
app.include_router(jobs.router)
app.include_router(job_matching.router)
app.include_router(career_advisor.router)
@app.get("/")
async def read_root():
    return {"Hello": "World"}