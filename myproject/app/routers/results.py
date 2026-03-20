from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter(tags=["Results"])


@router.get("/results/{requirement_id}")
def get_results(
    requirement_id: str,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    jd = db.query(models.JobDescription).filter(
        models.JobDescription.requirement_id == requirement_id
    ).first()

    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    results = (
        db.query(models.Resume, models.ScreenResult)
        .join(models.ScreenResult, models.Resume.resume_id == models.ScreenResult.resume_id)
        .filter(models.ScreenResult.jd_id == jd.jd_id)
        .order_by(models.ScreenResult.match_score.desc(), models.ScreenResult.created_at.desc())
        .limit(top_n)
        .all()
    )

    response = []

    for resume, result in results:
        response.append({
            "resume_id": str(resume.resume_id),
            "candidate_name": resume.name,
            "resume_name": str(resume.resume_id),
            "score": result.match_score,
            "skills_match": result.skills_match.split(",") if result.skills_match else [],
            "experience": float(resume.years_of_experience) if resume.years_of_experience is not None else None,
            "summary": result.summary,
        })

    return {
        "requirement_id": requirement_id,
        "results": response,
    }
