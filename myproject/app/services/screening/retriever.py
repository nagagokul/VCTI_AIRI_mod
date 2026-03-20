from collections import defaultdict
from sqlalchemy import select
from ...database import SessionLocal
from ...models import Resume, ResumeChunk, JobDescription
from ..core.resume_deduplication import FINGERPRINT_SECTION
from ..ai.embedding.embedding_service import get_embedding_provider


class ResumeRetriever:

    SECTION_WEIGHTS = {
        "experience": 0.4,
        "projects": 0.3,
        "skills": 0.2,
        "education": 0.1
    }

    def __init__(self):
        self.embedding_provider = get_embedding_provider()


    def build_context(self, rows, match_scores):
        context_parts = []
        last_resume_id = None

        for row in rows:

            (
                resume_id,
                name,
                email,
                phone,
                linkedin,
                github,
                location,
                years_of_experience,
                section,
                content
            ) = row

            email = email or "N/A"
            phone = phone or "N/A"
            linkedin = linkedin or "N/A"
            github = github or "N/A"
            location = location or "N/A"
            years_of_experience = years_of_experience or 0.0

            score = match_scores.get(resume_id, 0)

            if resume_id != last_resume_id:

                context_parts.append(
                    f"resume_id: {resume_id}\n"
                    f"Candidate: {name} ({email})\n"
                    f"Phone: {phone}, LinkedIn: {linkedin}, GitHub: {github}\n"
                    f"Location: {location}, Experience: {years_of_experience} years\n"
                    f"embedding_similarity_score: {score:.2f}"
                )

                last_resume_id = resume_id

            context_parts.append(
                f"Section: {section}\n"
                f"Content:\n{content}\n"
            )

        return "\n".join(context_parts)

    # -------------------------
    # Fetch Job Description
    # -------------------------
    def get_job_context(self, job_id):

        with SessionLocal() as db:

            stmt = (
                select(
                    JobDescription.job_description,
                    JobDescription.required_skills,
                    JobDescription.experience_level
                )
                .where(JobDescription.jd_id == job_id)
            )

            result = db.execute(stmt).first()

        if not result:
            return ""

        job_description, skills, exp = result

        return f"""
        Job Description:
        {job_description}

        Required Skills:
        {skills}

        Experience Level:
        {exp}
        """

    # -------------------------
    # Retrieve Similar Resumes
    # -------------------------
    def retrieve_resume_ids(self, resume_ids, query_vector, top_k, threshold):

        with SessionLocal() as db:

            similarity = 1 - ResumeChunk.embedding.cosine_distance(query_vector)

            stmt = (
                select(
                    ResumeChunk.resume_id,
                    ResumeChunk.section,
                    similarity.label("similarity")
                )
                .where(ResumeChunk.resume_id.in_(resume_ids))
                .where(ResumeChunk.section != FINGERPRINT_SECTION)
            )

            rows = db.execute(stmt).all()

        resume_scores = defaultdict(float)

        for resume_id, section, similarity in rows:
            weight = self.SECTION_WEIGHTS.get(section.lower(), 0)
            resume_scores[resume_id] += similarity * weight

        filtered = {
            rid: score for rid, score in resume_scores.items()
            if score > threshold
        }

        top_resume_ids = sorted(
            filtered,
            key=lambda x: filtered[x],
            reverse=True
        )[:top_k]

        return top_resume_ids, filtered

    # -------------------------
    # Fetch Resume Data
    # -------------------------
    def fetch_resume_data(self, resume_ids):

        if not resume_ids:
            return []

        with SessionLocal() as db:

            stmt = (
                select(
                    Resume.resume_id,
                    Resume.name,
                    Resume.email,
                    Resume.phone,
                    Resume.linkedin,
                    Resume.github,
                    Resume.location,
                    Resume.years_of_experience,
                    ResumeChunk.section,
                    ResumeChunk.content
                )
                .join(ResumeChunk)
                .where(Resume.resume_id.in_(resume_ids))
                .where(ResumeChunk.section != FINGERPRINT_SECTION)
                .order_by(Resume.resume_id, ResumeChunk.section)
            )

            rows = db.execute(stmt).all()

        return rows

    # -------------------------
    # Main Retrieval
    # -------------------------
    def retrieve_context(self, job_id, resume_ids, top_k=5, threshold=0.3):

        job_description = self.get_job_context(job_id)

        query_vector = self.embedding_provider.generate(job_description)

        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()

        top_resume_ids, resume_scores = self.retrieve_resume_ids(
            resume_ids,
            query_vector,
            top_k,
            threshold
        )

        rows = self.fetch_resume_data(top_resume_ids)
        context =  self.build_context(rows, resume_scores)
        return job_description, context