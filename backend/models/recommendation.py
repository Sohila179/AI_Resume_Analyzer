from sqlalchemy import Column, Integer, String, ForeignKey, Float,JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id")
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id")
    )

    score: Mapped[float] = mapped_column(Float, index=True)
    reason: Mapped[str] = mapped_column(String, index=True)
    
    matched_skills: Mapped[list[str]] = mapped_column(JSON)
    missing_skills: Mapped[list[str]] = mapped_column(JSON)
    resume: Mapped["Resume"] = relationship(
        back_populates="recommendations"
    )

    job: Mapped["Job"] = relationship(
        back_populates="recommendations"
    )
