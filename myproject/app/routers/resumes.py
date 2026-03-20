from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
import os
import uuid
import shutil
from pathlib import Path
import json

from ..services.pipeline.chain_builder import ResumePipelineBuilder
from ..services.core.resume_db_mapper import map_to_db_models
from ..services.core.resume_deduplication import (
    FINGERPRINT_SECTION,
    build_fingerprint_payload,
    build_resume_canonical_text,
    decide_resume_action,
    fingerprint_to_content,
)
from ..routers.screening import refresh_screening_results

router = APIRouter(prefix="/resumes", tags=["Resumes"])
UPLOAD_DIR = "app/uploads/resumes"
JSON_DIR = "app/uploads/json"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


@router.post("/upload")
def upload_resumes(
    requirement_id: str = Form(...),
    resumes: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    uploaded: list[str] = []
    updated: list[str] = []
    duplicates: list[dict] = []
    refresh_candidates: list[str] = []

    jd = db.query(models.JobDescription).filter(
        models.JobDescription.requirement_id == requirement_id
    ).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    resume_pipeline = ResumePipelineBuilder().build_structure_json_pipeline()

    for file in resumes:
        uid = uuid.uuid4()
        unique_name = f"{uid}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        raw_output = resume_pipeline.invoke({"path": file_path})
        resume_json = raw_output.get("filled_resume")

        json_name = f"{uid}_{Path(file.filename).stem}.json"
        json_path = os.path.join(JSON_DIR, json_name)

        if not resume_json:
            raise HTTPException(status_code=422, detail=f"Pipeline returned empty result for: {file.filename}")

        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(resume_json, handle, ensure_ascii=False, indent=4)

        resume, chunks = map_to_db_models(resume_json)
        canonical_text = build_resume_canonical_text(resume_json)
        fingerprint = build_fingerprint_payload(canonical_text)
        decision = decide_resume_action(db, resume, fingerprint)

        if decision.action == "duplicate":
            duplicates.append({
                "file_name": file.filename,
                "existing_resume_id": str(decision.existing_resume.resume_id) if decision.existing_resume else None,
                "similarity": round(decision.similarity, 4),
                "message": "Duplicate resume rejected",
            })
            continue

        target_resume: Optional[models.Resume] = decision.existing_resume
        action = "created"

        if target_resume is None:
            target_resume = models.Resume()
            db.add(target_resume)
            db.flush()
        else:
            action = "updated"
            (
                db.query(models.ScreenResult)
                .filter(
                    models.ScreenResult.resume_id == target_resume.resume_id,
                    models.ScreenResult.jd_id == jd.jd_id,
                )
                .delete(synchronize_session=False)
            )
            (
                db.query(models.ResumeChunk)
                .filter(models.ResumeChunk.resume_id == target_resume.resume_id)
                .delete(synchronize_session=False)
            )

        target_resume.name = resume.name
        target_resume.email = resume.email
        target_resume.phone = resume.phone
        target_resume.linkedin = resume.linkedin
        target_resume.github = resume.github
        target_resume.location = resume.location
        target_resume.years_of_experience = resume.years_of_experience
        db.flush()

        for chunk in chunks:
            db.add(models.ResumeChunk(
                resume_id=target_resume.resume_id,
                section=chunk.section,
                content=chunk.content,
                embedding=chunk.embedding,
            ))

        db.add(models.ResumeChunk(
            resume_id=target_resume.resume_id,
            section=FINGERPRINT_SECTION,
            content=fingerprint_to_content(fingerprint),
            embedding=None,
        ))

        if action == "created":
            uploaded.append(str(target_resume.resume_id))
        else:
            updated.append(str(target_resume.resume_id))

        refresh_candidates.append(str(target_resume.resume_id))

    db.commit()

    refreshed_results = []
    if refresh_candidates:
        refreshed_results = refresh_screening_results(
            db=db,
            jd=jd,
            resume_ids=refresh_candidates,
        )

    return {
        "uploaded": uploaded,
        "updated": updated,
        "duplicates": duplicates,
        "screening_refreshed_for": refresh_candidates,
        "screening_results": refreshed_results,
    }
