from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base

class CareerAdvisor(Base):
    __tablename__ = "career_advisors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    missing_skills: Mapped[str] = mapped_column(String, index=True)
    courses: Mapped[str] = mapped_column(String, index=True)
    certifications: Mapped[str] = mapped_column(String, index=True)
    learning_resources: Mapped[str] = mapped_column(String, index=True)
    career_questions: Mapped[str] = mapped_column(String, index=True)

    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"))
    resume: Mapped["Resume"] = relationship(back_populates="career_advisor")
