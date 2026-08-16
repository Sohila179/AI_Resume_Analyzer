from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="job_seeker")

    resumes: Mapped[list["Resume"]] = relationship(
        "Resume",
        back_populates="user"
    )

    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="employer"
    )