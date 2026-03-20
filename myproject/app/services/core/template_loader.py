import json
from pathlib import Path


class ResumeTemplateLoader:

    def __init__(self, template_path: str):
        self.template_path = Path(template_path)

    def load(self) -> dict:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_sections(self) -> dict:
        resume = self.load()

        return {
            "personal_info": resume.get("personal_info", {}),
            "skills": resume.get("skills", {}),
            "experience": resume.get("experience", []),
            "projects": resume.get("projects", []),
            "education": resume.get("education", []),
            "certifications": resume.get("certifications", [])
        }