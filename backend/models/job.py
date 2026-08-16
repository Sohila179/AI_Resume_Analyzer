from sqlalchemy import Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(String)
    required_skills: Mapped[list[str]] = mapped_column(JSON)

    employer: Mapped["User"] = relationship(
        "User",
        back_populates="jobs"
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="job"
    )