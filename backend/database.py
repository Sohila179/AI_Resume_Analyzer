from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Settings
from sqlalchemy.ext.declarative import declarative_base

settings=Settings()

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()
