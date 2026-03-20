from ..core.template_loader import ResumeTemplateLoader
from ..core.section_mapper import SectionMapper
from ..core.json_section_filler import JSONSectionFiller
from ..parsing.pdf_parser import PDFParser
from ..prompt_templates.prompts import prompt_map
from langchain_core.runnables import RunnableLambda
from ...config import settings
class RunnableFactory:

    def __init__(self):
        template_loader = ResumeTemplateLoader(settings.json_template_path)
        self.section_templates = template_loader.get_sections()

        self.parser = PDFParser()
        self.section_mapper = SectionMapper()

        self.section_filler = JSONSectionFiller(
            llm=None,
            prompt_map=prompt_map
        )

    def build(self, llm_json):
        self.section_filler.llm = llm_json

        # Extract resume text from file
        extract_resume = RunnableLambda(
            lambda resume_input: {
                "resume_text": self.parser.hybrid_resume_parser(
                    resume_input["path"]
                )
            }
        )

        # Map structured sections from LLM output
        map_sections = RunnableLambda(
            lambda pipeline_state: {
                "mapped_content": self.section_mapper.map(
                    pipeline_state.content 
                )
            }
        )

        # Fill final JSON resume structure
        fill_resume_json = RunnableLambda(
            lambda pipeline_state: {
                "filled_resume": self.section_filler.fill(
                    sections_template=self.section_templates,
                    mapped_sections= pipeline_state["mapped_content"]
                )
            }
        )

        self.extract_resume_runnable = extract_resume
        self.map_sections_runnable = map_sections
        self.fill_resume_runnable = fill_resume_json

        return self