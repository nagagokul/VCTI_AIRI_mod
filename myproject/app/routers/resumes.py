from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
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
    # reset for every  upload to track current upload
    uploaded = []  

    # llm parsing chain
    resume_pipeline  = ResumePipelineBuilder().build_structure_json_pipeline()
    
    
    for file in resumes:
        uid =uuid.uuid4()
        unique_name = f"{uid}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        #  llm json out
        raw_output = resume_pipeline.invoke({"path": file_path})
        resume_json = raw_output.get("filled_resume")


        json_name = f"{uid}_{Path(file.filename).stem}.json"
        json_path = os.path.join(JSON_DIR, json_name)


        if not resume_json:
            raise ValueError(f"Pipeline returned empty result for: {file.filename}")
        else:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(resume_json, f, ensure_ascii=False, indent=4)

        # resume_json mapped with pydantic Resume 
        resume, chunks = map_to_db_models(resume_json)

        resume_db = models.Resume(
            name = resume.name,
            email = resume.email,
            phone = resume.phone,
            linkedin = resume.linkedin,
            github = resume.github,
            location = resume.location,
            years_of_experience = resume.years_of_experience  
        )

        db.add(resume_db)
        db.flush()  # DB assigns resume_id 

        for chunk in chunks:
            db.add(models.ResumeChunk(
                resume_id = resume_db.resume_id,
                section = chunk.section,
                content = chunk.content,
                embedding = chunk.embedding
            ))
        uploaded.append(str(resume_db.resume_id))
    db.commit()

    return {
        "uploaded": uploaded
    }


"""
we aren't savind data in db ?
so, not  retreivable via resume_id/candidate id.
"""
# @router.get("/resume/{resume_id}/download")
# def download_resume(resume_id: int, db: Session = Depends(get_db)):

#     resume_record = db.query(models.Resume).filter(
#         models.Resume.resume_id == resume_id
#     ).first()

#     # NOTE: db model does not contain file path so using a placeholder property, 
#     # but querying the Resume table as requested.
#     path = f"app/uploads/resumes/{getattr(resume_record, 'resume_filename', 'unknown.pdf')}"

#     return FileResponse(path, filename=candidate.resume_filename)