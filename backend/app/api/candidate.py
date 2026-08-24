from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from backend.app.database import get_db
from backend.app.models.candidate import Candidate
from backend.app.schemas.candidate import CandidateCreate, CandidateScore
from backend.app.services.scoring import score_candidate


router = APIRouter()


# ==========================================
# GET ALL CANDIDATES
# ==========================================

@router.get("/")
def get_candidates(db: Session = Depends(get_db)):

    candidates = db.query(Candidate).all()

    result = []

    for candidate in candidates:

        try:
            skills = (
                json.loads(candidate.skills)
                if candidate.skills
                else []
            )
        except (json.JSONDecodeError, TypeError):
            skills = []

        result.append({
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "skills": skills,
            "education": candidate.education,
            "experience": candidate.experience,
            "overall_score": candidate.overall_score,
            "resume_filename": candidate.resume_filename
        })

    return result


# ==========================================
# CREATE CANDIDATE
# ==========================================

@router.post("/")
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):

    new_candidate = Candidate(
        name=candidate.name,
        email=candidate.email,
        skills=json.dumps(candidate.skills)
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return {
        "id": new_candidate.id,
        "name": new_candidate.name,
        "email": new_candidate.email,
        "skills": json.loads(new_candidate.skills),
        "overall_score": new_candidate.overall_score
    }


# ==========================================
# SCORE CANDIDATE
# ==========================================

@router.post("/score")
def score_candidate_api(
    request: CandidateScore,
    db: Session = Depends(get_db)
):

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == request.candidate_id)
        .first()
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    try:

        candidate_skills = (
            json.loads(candidate.skills)
            if candidate.skills
            else []
        )

    except (json.JSONDecodeError, TypeError):

        candidate_skills = []

    result = score_candidate(
        candidate_skills,
        request.required_skills
    )

    candidate.overall_score = result["score"]

    db.commit()
    db.refresh(candidate)

    return {
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "score": result["score"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"]
    }


# ==========================================
# GET RANKED CANDIDATES
# ==========================================

@router.get("/ranked")
def get_ranked_candidates(db: Session = Depends(get_db)):

    candidates = (
        db.query(Candidate)
        .order_by(Candidate.overall_score.desc())
        .all()
    )

    result = []

    for candidate in candidates:

        try:

            skills = (
                json.loads(candidate.skills)
                if candidate.skills
                else []
            )

        except (json.JSONDecodeError, TypeError):

            skills = []

        result.append({
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "skills": skills,
            "overall_score": candidate.overall_score,
            "resume_filename": candidate.resume_filename
        })

    return result


# ==========================================
# GET ONE CANDIDATE
# ==========================================

@router.get("/{candidate_id}")
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    try:

        skills = (
            json.loads(candidate.skills)
            if candidate.skills
            else []
        )

    except (json.JSONDecodeError, TypeError):

        skills = []

    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "skills": skills,
        "education": candidate.education,
        "experience": candidate.experience,
        "overall_score": candidate.overall_score,
        "resume_filename": candidate.resume_filename
    }


# ==========================================
# DELETE ONE CANDIDATE
# ==========================================

@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    db.delete(candidate)

    db.commit()

    return {
        "message": "Candidate deleted successfully"
    }


# ==========================================
# DELETE ALL CANDIDATES
# ==========================================

@router.delete("/")
def delete_all_candidates(
    db: Session = Depends(get_db)
):

    db.query(Candidate).delete()

    db.commit()

    return {
        "message": "All candidates deleted successfully"
    }