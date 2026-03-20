from langchain_core.prompts import ChatPromptTemplate
from app.services.prompt_templates.arrange import SYSTEM_PROMPT_STRUCT, HUMAN_PROMPT_STRUCT
from app.services.prompt_templates.structure import personal_info_prompt, skills_prompt, experience_prompt,projects_prompt, education_prompt, certifications_prompt
from app.services.prompt_templates.screen import system_screening_prompt, human_screening_prompt

prompt_arrange = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT_STRUCT),
    ("human", HUMAN_PROMPT_STRUCT)
])

prompt_map = {
    "personal_info": personal_info_prompt,
    "skills": skills_prompt,
    "experience": experience_prompt,
    "projects": projects_prompt,
    "education": education_prompt,
    "certifications": certifications_prompt
}


screening_template =  ChatPromptTemplate.from_messages([
    ("system",system_screening_prompt),
    ("human", human_screening_prompt)
])