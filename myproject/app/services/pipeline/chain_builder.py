from .runnable_factory import RunnableFactory
from ..prompt_templates.prompts import prompt_arrange
from app.config import settings
from ..ai.llm.llm_provider import LLMProvider

class ResumePipelineBuilder:

    def __init__(self):
        self.LLM_ARRANGE =  LLMProvider(settings.arrange_llm).get_client()
        self.LLM_STRUCT = LLMProvider(settings.arrange_llm).get_client()

        self.runnable_factory = RunnableFactory().build(llm_json=self.LLM_STRUCT)
        
        self._arrange_chain = None
        self._mapped_chain = None

    def build_arranging_stage(self):
        if self.LLM_ARRANGE is None:
            raise ValueError("ARRANGE LLM is not defined")
        
        self._arrange_chain = self.runnable_factory.extract_resume_runnable| prompt_arrange | self.LLM_ARRANGE
        return self._arrange_chain

    def build_section_mapping_stage(self):
        if self._mapped_chain:
            return self._mapped_chain

        self._mapped_chain = (
            self.build_arranging_stage()
            | self.runnable_factory.map_sections_runnable
        )
        return self._mapped_chain

    def build_structure_json_pipeline(self):
        if self.LLM_STRUCT is None:
            raise ValueError("STRUCT LLM is not defined")
        
        return (
            self.build_section_mapping_stage()
            | self.runnable_factory.fill_resume_runnable
        )