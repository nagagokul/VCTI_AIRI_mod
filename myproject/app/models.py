from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Numeric
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid


# =========================
# USERS
# =========================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    job_descriptions = relationship(
        "JobDescription",
        back_populates="user"
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user"
    )


# =========================
# REFRESH TOKENS
# =========================

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

    user = relationship("User", back_populates="refresh_tokens")


# =========================
# JOB DESCRIPTIONS
# =========================

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    jd_id = Column(Integer, primary_key=True)
    requirement_id = Column(String, unique=True)
    job_title = Column(String)
    job_description = Column(Text)
    experience_level = Column(String)
    required_skills = Column(Text)

    user_id = Column(Integer, ForeignKey("users.user_id"))

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )

    user = relationship("User", back_populates="job_descriptions")

    screen_results = relationship(
        "ScreenResult",
        back_populates="job",
        cascade="all, delete"
    )


# =========================
# RESUMES
# =========================

class Resume(Base):
    __tablename__ = "resumes"

    resume_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    name = Column(Text)
    email = Column(Text, unique=True)
    phone = Column(Text)
    linkedin = Column(Text)
    github = Column(Text)
    location = Column(Text)

    years_of_experience = Column(Numeric(4, 1))

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    chunks = relationship(
        "ResumeChunk",
        back_populates="resume",
        cascade="all, delete"
    )

    screen_results = relationship(
        "ScreenResult",
        back_populates="resume",
        cascade="all, delete"
        
    )


# =========================
# RESUME CHUNKS (AI embeddings)
# =========================

class ResumeChunk(Base):
    __tablename__ = "resume_chunks"

    chunk_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        nullable=False
    )

    section = Column(Text)
    content = Column(Text)
    embedding = Column(Vector(1024))

    resume = relationship(
        "Resume",
        back_populates="chunks"
    )


# =========================
# SCREEN RESULTS
# =========================

class ScreenResult(Base):
    __tablename__ = "screen_results"

    screen_result_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        nullable=False
    )

    jd_id = Column(
        Integer,
        ForeignKey("job_descriptions.jd_id", ondelete="CASCADE"),
        nullable=False
    )

    match_score = Column(Integer)
    skills_match = Column(Text)
    summary = Column(Text)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    resume = relationship("Resume", back_populates="screen_results")
    job = relationship("JobDescription", back_populates="screen_results")