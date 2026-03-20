system_screening_prompt = """
You are an expert technical recruiter AI.
Use ONLY the provided resume context.
If the answer is missing for a candidate, return an empty list [].
"""

human_screening_prompt = """
CONTEXT:
{context}

JOB DESCRIPTION / QUESTION:
{job_description}

Instructions:
For each candidate mentioned in the context who has relevant skills or experience, return a JSON array where each element has the following structure:
[
  {{
    "resume_id": "the resume_id from the candidate context",
    "candidate_name": "Full Name",
    "score": 0-100,
    "skills_match": "Comma-separated list of matching skills from the job description",
    "experience": "Brief summary of relevant experience years and roles",
    "summary": "Short overall summary of how well the candidate matches the job"
  }}
]

Notes:
- If a candidate does not match at all, exclude them from the array.
- Include all candidates even with low score.
- `skills_match` should reflect only skills mentioned in both the resume and job description.
- `experience` should be a short string like "3 years in backend development, worked with Python and AWS".
- `summary` should be 1-2 sentences describing overall fit.
- Return **valid JSON only**, no extra text, no markdown, no numbering.
"""