from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship,mapped_column,Mapped
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    resumes:Mapped[list["Resume"]] = relationship("Resume", back_populates="user")