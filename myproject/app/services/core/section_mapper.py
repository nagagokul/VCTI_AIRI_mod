class SectionMapper:

    def __init__(self):
        self.key_map = {
            'name': 'personal_info',
            'contact information': 'personal_info',
            'education': 'education',
            'key courses taken': 'education',
            'experience': "experience",
            'projects': "projects",
            'skills': "skills",
            'certifications': "certifications",
            'positions of responsibility': "certifications",
            'awards / miscellaneous': "certifications"
        }

    def map(self, raw_text: str) -> dict:

        mapped = {v: "" for v in set(self.key_map.values())}

        chunks = [
            s.strip() for s in raw_text.split("=######=") if s.strip()
        ]

        for chunk in chunks:

            first_line = chunk.split("\n")[0].strip().lower()

            target_key = "personal_info"

            for k, v in self.key_map.items():
                if k in first_line:
                    target_key = v
                    break

            mapped[target_key] += chunk + "\n"

        return {k: v.strip() for k, v in mapped.items()}