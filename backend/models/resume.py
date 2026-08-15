from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    id: Mapped[int] =mapped_column(Integer,primary_key=True,index=True)
    resume_file: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="resumes")

    resume_analysis: Mapped["AnalysisResume"] = relationship( back_populates="resume")

    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="resume")

    career_advisor: Mapped["CareerAdvisor"] = relationship(back_populates="resume")