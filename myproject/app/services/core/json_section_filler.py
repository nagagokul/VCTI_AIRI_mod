import json

class JSONSectionFiller:
    
    def __init__(self, llm, prompt_map):
        self.llm = llm
        self.prompt_map = prompt_map

    def _fill_single_section(
        self,
        section_name,
        template_json,
        section_text
        ):

        prompt = self.prompt_map[section_name].format(
            template_json=json.dumps(template_json, indent=2),
            section_text=section_text
        )

        response = self.llm.invoke(prompt)

        try:
            return json.loads(response.content)
        except Exception:
            return template_json

    def fill(self, sections_template, mapped_sections):

        filled = {}

        for key in sections_template:

            filled[key] = self._fill_single_section(
                section_name=key,
                template_json=sections_template[key],
                section_text=mapped_sections[key],
            )

        return filled