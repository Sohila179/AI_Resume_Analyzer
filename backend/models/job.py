from sqlalchemy import Column, Integer, String, ForeignKey ,JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(String, index=True)
    required_skills: Mapped[list[str]] = mapped_column(JSON)
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="job")
    