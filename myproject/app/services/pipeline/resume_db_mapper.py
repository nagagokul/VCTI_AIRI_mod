from uuid import uuid4
from datetime import datetime
from ...schemas import ResumeChunk, Resume
from ...services.ai.embedding.embedding_service import get_embedding_provider

def calculate_years_of_experience(experiences):
    total_months = 0
    now = datetime.now()

    for exp in experiences:
        start = exp.get("start_date")
        end = exp.get("end_date")
        is_current = exp.get("is_current", False)

        if not start:
            continue

        try:
            start_date = datetime.strptime(start, "%m.%Y")

            if is_current or not end:
                end_date = now
            else:
                end_date = datetime.strptime(end, "%m.%Y")

            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

            if months > 0:
                total_months += months

        except Exception:
            continue  # skip invalid dates safely

    return round(total_months / 12, 1)  # return years as float (e.g., 3.5)

def map_to_db_models(data: dict):
    """
    Map parsed resume JSON to DB models (Resume + ResumeChunk) with embeddings.
    """
    personal = data.get("personal_info", {})


    # Calculate experience here
    experiences = data.get("experience", [])
    years_of_experience = calculate_years_of_experience(experiences)

    resume = Resume(
        name=personal.get("name"),
        email=personal.get("email"),
        phone=personal.get("phone"),
        linkedin=personal.get("linkedin"),
        github=personal.get("github"),
        location=personal.get("location"),
        years_of_experience=years_of_experience  
    )

    def join_text(items):
        if not items:
            return ""
        return "\n".join(str(i) for i in items if i)

    # Collect sections
    sections = {}

    # Experience
    sections["experience"] = join_text(
        f"{e.get('company','')} {e.get('role','')} " + join_text(e.get("responsibilities", []))
        for e in experiences
    )

    # Projects
    sections["projects"] = join_text(
        p.get("name","") + " " + join_text(p.get("description", []))
        for p in data.get("projects", [])
    )

    # Skills
    skills = data.get("skills", {}).get("technical", [])
    sections["skills"] = ", ".join(skills) if skills else ""

    # Education
    sections["education"] = join_text(
        e.get("degree","") + " " + e.get("institution","")
        for e in data.get("education", [])
    )

    # Batch embedding
    section_texts = list(sections.values())
    embedding_generator = get_embedding_provider()
    embeddings = embedding_generator.batch_generate(section_texts)

    chunks = []
    for (section_name, text), vector in zip(sections.items(), embeddings):
        chunks.append(
            ResumeChunk(
                section=section_name,
                content=text,
                embedding=vector,
            )
        )

    return resume, chunks