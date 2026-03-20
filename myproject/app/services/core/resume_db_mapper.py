from datetime import datetime

from pydantic import EmailStr, TypeAdapter, ValidationError

from ...schemas import Resume, ResumeChunk
from ..ai.embedding.embedding_service import get_embedding_provider

EMAIL_ADAPTER = TypeAdapter(EmailStr)


def normalize_optional_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_optional_email(value):
    text = normalize_optional_text(value)
    if not text:
        return None
    try:
        return str(EMAIL_ADAPTER.validate_python(text))
    except ValidationError:
        return None


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%m.%Y")
    except Exception:
        return None


def calculate_years_of_experience(experiences):
    now = datetime.now()
    ranges = []

    experiences = sorted(
        experiences,
        key=lambda x: parse_date(x.get("start_date")) or datetime.max,
    )

    for i, exp in enumerate(experiences):
        start = parse_date(exp.get("start_date"))
        end = parse_date(exp.get("end_date"))

        if not start:
            continue

        if exp.get("is_current"):
            end = now
        elif not end and i + 1 < len(experiences):
            next_start = parse_date(experiences[i + 1].get("start_date"))
            if next_start:
                end = next_start

        if not end or start >= end:
            continue

        ranges.append((start, end))

    if not ranges:
        return 0.0

    ranges.sort(key=lambda x: x[0])
    merged = [ranges[0]]

    for curr_start, curr_end in ranges[1:]:
        last_start, last_end = merged[-1]

        if curr_start <= last_end:
            merged[-1] = (last_start, max(last_end, curr_end))
        else:
            merged.append((curr_start, curr_end))

    total_months = 0
    for start, end in merged:
        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += months

    return round(total_months / 12, 1)


def map_to_db_models(data: dict, embedding_model=None):
    """
    Map parsed resume JSON to DB models (Resume + ResumeChunk) with embeddings.
    Blank or invalid contact fields are normalized to None so OCR/parser noise
    does not break resume ingestion.
    """
    embedding = embedding_model or get_embedding_provider()
    personal = data.get("personal_info", {})

    experiences = data.get("experience", [])
    years_of_experience = calculate_years_of_experience(experiences)

    resume = Resume(
        name=normalize_optional_text(personal.get("name")),
        email=normalize_optional_email(personal.get("email")),
        phone=normalize_optional_text(personal.get("phone")),
        linkedin=normalize_optional_text(personal.get("linkedin")),
        github=normalize_optional_text(personal.get("github")),
        location=normalize_optional_text(personal.get("location")),
        years_of_experience=years_of_experience,
    )

    def join_text(items):
        if not items:
            return ""
        return "\n".join(str(item) for item in items if item)

    sections = {}
    sections["experience"] = join_text(
        f"{exp.get('company', '')} {exp.get('role', '')} " + join_text(exp.get("responsibilities", []))
        for exp in experiences
    )
    sections["projects"] = join_text(
        project.get("name", "") + " " + join_text(project.get("description", []))
        for project in data.get("projects", [])
    )

    skills = data.get("skills", {}).get("technical", [])
    sections["skills"] = ", ".join(skills) if skills else ""
    sections["education"] = join_text(
        education.get("degree", "") + " " + education.get("institution", "")
        for education in data.get("education", [])
    )

    section_texts = list(sections.values())
    embeddings = embedding.batch_generate(section_texts)

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
