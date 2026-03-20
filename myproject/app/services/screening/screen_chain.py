from langchain_core.runnables  import RunnableLambda
from .retriever import  ResumeRetriever
from ..prompt_templates.prompts import screening_template
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from ..ai.llm.llm_service import get_llm

class ScreeningChain:

    def __init__(self):
        self.llm = get_llm()
        self.retriever = ResumeRetriever()

    def retrieve_and_prepare(self, inputs):

        job_id = inputs["job_id"]
        resume_ids = inputs["resume_ids"]

        job_description,context = self.retriever.retrieve_context(
            job_id,
            resume_ids
        )


        if not context.strip():

            return {
                "context": "",
                "job_description": job_description,
            }

        return {
            "context": context,
            "job_description": job_description,
        }

    def build_chain(self):

        return (
            RunnableLambda(self.retrieve_and_prepare)
            | screening_template
            | self.llm
            | JsonOutputParser()
        )