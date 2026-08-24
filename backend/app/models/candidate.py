from sqlalchemy import Column, Integer, String, Float, Text
from backend.app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)

    skills = Column(Text, nullable=True)

    education = Column(String, nullable=True)
    experience = Column(String, nullable=True)

    overall_score = Column(Float, default=0.0)

    resume_filename = Column(String, nullable=True)