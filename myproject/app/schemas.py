from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional,List
from pydantic import ConfigDict
from uuid import UUID

class UserOut(BaseModel):
    user_id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(...,min_length=8, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id:int

class TokenData(BaseModel):
    user_id: Optional[int] = None

class RefreshRequest(BaseModel):
    refresh_token: str

# JD upload
class JobDescriptionCreate(BaseModel):
    requirement_id: str
    job_title: str
    job_description: str
    experience_level: str
    required_skills: List[str]

class JobDescriptionOut(BaseModel):
    id: int
    requirement_id: str
    job_title: str
    job_description: str
    experience_level: str
    required_skills: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Screening request
class ScreenRequest(BaseModel):
    requirement_id: str
    # resume_ids: List[UUID]

# Result response
class ResultCandidate(BaseModel):
    candidate_name: Optional[str]
    resume_name: str
    score: int
    skills_match: List[str]
    experience: Optional[float] 

# Resume Personal info
class Resume(BaseModel):
    name: Optional[str] = None
    # Contact
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    # Profiles
    linkedin: Optional[str] = None
    github: Optional[str] = None

    # Location
    location: Optional[str] = None

    # Experience
    years_of_experience: Optional[float] = Field(
        None,
        ge=0,
        description="Total professional experience in years"
    )

    model_config = {
        "from_attributes": True
    }

# Resume's chunks
class ResumeChunk(BaseModel):
    section: Optional[str]
    content: Optional[str]
    embedding: Optional[List[float]] = None
    model_config = {
        "from_attributes": True
    }
    