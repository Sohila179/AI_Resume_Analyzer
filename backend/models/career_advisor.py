from sqlalchemy import Column, Integer, String, ForeignKey,JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base

class CareerAdvisor(Base):
    __tablename__ = "career_advisors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    missing_skills: Mapped[list[str]] = mapped_column(JSON)
    courses: Mapped[list[str]] = mapped_column(JSON)
    certifications: Mapped[list[str]] = mapped_column(JSON)
    learning_resources: Mapped[list[str]] = mapped_column(JSON)
    career_questions: Mapped[list[str]] = mapped_column(JSON)

    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"))
    resume: Mapped["Resume"] = relationship(back_populates="career_advisor")
