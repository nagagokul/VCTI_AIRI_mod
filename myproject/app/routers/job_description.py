from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..oauth2 import get_current_user

router = APIRouter(prefix="/jd", tags=["Job Description"])


@router.post("/")
def upload_jd(
    jd: schemas.JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    new_jd = models.JobDescription(
        requirement_id=jd.requirement_id,
        job_title=jd.job_title,
        job_description=jd.job_description,
        experience_level=jd.experience_level,
        required_skills=",".join(jd.required_skills),
        user_id=current_user.user_id
    )

    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)

    return new_jd


@router.get("/user")
def get_user_jds(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    jds = db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.user_id
    ).all()

    return [schemas.JobDescriptionOut.model_validate(jd) for jd in jds]