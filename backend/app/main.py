from fastapi import FastAPI

from backend.app.database import Base, engine
from backend.app.api.candidate import router as candidate_router
from backend.app.api.resume import router as resume_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Smart Resume Screener API",
    version="1.0.0",
    description="AI-powered candidate screening and ranking system"
)


app.include_router(
    candidate_router,
    prefix="/api/candidates",
    tags=["Candidates"]
)


app.include_router(
    resume_router,
    prefix="/api/resumes",
    tags=["Resume"]
)


@app.get("/")
def home():
    return {
        "message": "Smart Resume Screener API is running"
    }