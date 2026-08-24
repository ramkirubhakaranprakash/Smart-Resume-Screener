from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

import os
import json
import re
import shutil

from pypdf import PdfReader

from backend.app.database import get_db
from backend.app.models.candidate import Candidate


router = APIRouter()


# --------------------------------
# PROJECT PATHS
# --------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../"
    )
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# --------------------------------
# KNOWN SKILLS
# --------------------------------

KNOWN_SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "FastAPI",
    "Django",
    "Flask",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "Git",
    "GitHub",
    "Docker",
    "AWS",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "OpenCV",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "YOLO",
    "YOLOv8"
]


# --------------------------------
# EXTRACT TEXT FROM PDF
# --------------------------------

def extract_text_from_pdf(file_path):

    try:

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not read PDF: {str(e)}"
        )


# --------------------------------
# EXTRACT SKILLS
# --------------------------------

def extract_skills(text):

    found_skills = []

    text_lower = text.lower()

    for skill in KNOWN_SKILLS:

        skill_lower = skill.lower()

        if skill_lower in text_lower:

            found_skills.append(skill)

    return list(set(found_skills))


# --------------------------------
# EXTRACT EMAIL
# --------------------------------

def extract_email(text):

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    emails = re.findall(
        pattern,
        text
    )

    if emails:
        return emails[0]

    return None


# --------------------------------
# EXTRACT PHONE NUMBER
# --------------------------------

def extract_phone(text):

    pattern = r"(?:\+91[\s-]?)?[6-9]\d{9}"

    phones = re.findall(
        pattern,
        text
    )

    if phones:
        return phones[0]

    return None


# --------------------------------
# UPLOAD RESUME
# --------------------------------

@router.post("/upload")
async def upload_resume(

    name: str = Form(...),

    file: UploadFile = File(...),

    db: Session = Depends(get_db)

):

    # Check if file exists
    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )


    # Check file type
    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are allowed"
        )


    # Create safe filename
    filename = file.filename.replace(
        " ",
        "_"
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    # Save uploaded PDF
    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {str(e)}"
        )


    # Extract text from PDF
    resume_text = extract_text_from_pdf(
        file_path
    )


    # Check whether text was extracted
    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from this PDF"
        )


    # Extract information
    skills = extract_skills(
        resume_text
    )

    email = extract_email(
        resume_text
    )

    phone = extract_phone(
        resume_text
    )


    # Create candidate
    new_candidate = Candidate(

        name=name,

        email=email,

        phone=phone,

        skills=json.dumps(skills),

        resume_filename=filename,

        overall_score=0
    )


    # Save candidate to database
    db.add(
        new_candidate
    )

    db.commit()

    db.refresh(
        new_candidate
    )


    # Return response
    return {

        "message": "Resume uploaded successfully",

        "candidate": {

            "id": new_candidate.id,

            "name": new_candidate.name,

            "email": new_candidate.email,

            "phone": new_candidate.phone,

            "skills": skills,

            "resume_filename": new_candidate.resume_filename,

            "overall_score": new_candidate.overall_score
        }
    }