from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base

class AnalysisResume(Base):
    __tablename__ = "analysis_resumes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skills: Mapped[str] = mapped_column(String, index=True)
    experience: Mapped[str] = mapped_column(String, index=True)
    education: Mapped[str] = mapped_column(String, index=True)
    summary: Mapped[str] = mapped_column(String, index=True)

    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"))
    resume: Mapped["Resume"] = relationship(back_populates="resume_analysis")