from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..services.screening.screen_chain import ScreeningChain
from ..oauth2 import get_current_user


router = APIRouter(tags=["Screening"])


@router.post("/screen")
def screen_resumes(
    request: schemas.ScreenRequest,
    db: Session = Depends(get_db),
):
    jd = db.query(models.JobDescription).filter(
        models.JobDescription.requirement_id == request.requirement_id
    ).first()

    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    screen_chain = ScreeningChain().build_chain()

    # current upload
    resume_ids = [str(res.resume_id)for res in db.query(models.Resume)]
    
    # resume_ids = request.resume_ids  

    screening_results = screen_chain.invoke({
        "job_id": jd.jd_id,
        "resume_ids": resume_ids
    })

    # Normalize parser output
    if isinstance(screening_results, dict) and "results" in screening_results:
        screening_results = screening_results["results"]

    if isinstance(screening_results, tuple):
        screening_results = list(screening_results)

    if not isinstance(screening_results, list):
        raise HTTPException(status_code=502, detail="Unexpected screening result format")

    results = []

    for raw in screening_results:
        if isinstance(raw, dict):
            result = raw
        elif isinstance(raw, (list, tuple)) and len(raw) >= 5:
            # support fallback positional data: [resume_id, candidate_name, score, skills_match, experience, summary]
            result = {
                "resume_id": raw[0],
                "candidate_name": raw[1],
                "score": raw[2],
                "skills_match": raw[3],
                "experience": raw[4],
                "summary": raw[5] if len(raw) > 5 else ""
            }
        else:
            # skip malformed item
            continue

        if "resume_id" not in result or "score" not in result:
            continue

        # coerce to desired types
        match_score = int(result.get("score", 0))
        skills_match_value = result.get("skills_match", "")

        screening_result = models.ScreenResult(
            resume_id=result["resume_id"],
            jd_id=jd.jd_id,
            match_score=match_score,
            skills_match=",".join(skills_match_value) if isinstance(skills_match_value, list) else str(skills_match_value),
            summary=str(result.get("summary", ""))
        )
        db.add(screening_result)

        results.append({
            "candidate": result["resume_id"],
            "score": match_score
        })

    db.commit()

    return {
        "message": "Screening completed",
        "results": results
    }