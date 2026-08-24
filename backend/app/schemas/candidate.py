from pydantic import BaseModel
from typing import List


class CandidateCreate(BaseModel):
    name: str
    email: str
    skills: List[str]


class CandidateScore(BaseModel):
    candidate_id: int
    required_skills: List[str]