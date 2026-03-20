from ...schemas import Resume, ResumeChunk
from datetime import datetime
from ..ai.embedding.embedding_service import get_embedding_provider


from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%m.%Y")
    except:
        return None

def calculate_years_of_experience(experiences):
    now = datetime.now()
    ranges = []

    # Step 1: Sort experiences by start date
    experiences = sorted(
        experiences,
        key=lambda x: parse_date(x.get("start_date")) or datetime.max
    )

    # Step 2: Build valid ranges
    for i, exp in enumerate(experiences):
        start = parse_date(exp.get("start_date"))
        end = parse_date(exp.get("end_date"))

        # No start → skip
        if not start:
            continue

        # Current job
        if exp.get("is_current"):
            end = now

        # Missing end → try infer
        elif not end:
            if i + 1 < len(experiences):
                next_start = parse_date(experiences[i + 1].get("start_date"))
                if next_start:
                    end = next_start

        #  Still invalid → skip
        if not end or start >= end:
            continue

        ranges.append((start, end))

    if not ranges:
        return 0.0

    # Step 3: Merge overlapping ranges
    ranges.sort(key=lambda x: x[0])
    merged = [ranges[0]]

    for curr_start, curr_end in ranges[1:]:
        last_start, last_end = merged[-1]

        if curr_start <= last_end:
            merged[-1] = (last_start, max(last_end, curr_end))
        else:
            merged.append((curr_start, curr_end))

    # Step 4: Calculate total months
    total_months = 0
    for start, end in merged:
        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += months

    return round(total_months / 12, 1)

def map_to_db_models(data: dict, embedding_model=None):
    """
    Map parsed resume JSON to DB models (Resume + ResumeChunk) with embeddings.
    """
    embedding = get_embedding_provider()
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