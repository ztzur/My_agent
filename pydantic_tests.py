import pandas as pd
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field, validator
from configs.general import config as c


# Define your desired data structure.
class TestResults(BaseModel):
    score: int = Field(description="the score of the test")
    justification: str = Field(description="the justification of the test score")


with open('configs/tests/sub_sal/prompts/team_competency.txt', 'r') as f:
    prompt = f.read()

programs = pd.read_csv(c.programs_path)
sub = pd.read_csv(c.subjects_path)

objective = programs.loc[0, 'מטרה מרכזית']
summary = programs.loc[0, 'תקציר תוכנית']
conditions = sub.loc[programs.loc[0, 'תת סל'] == sub['Name'], 'Min_conditions'].values[0]

# Set up a parser + inject instructions into the prompt template.
parser = PydanticOutputParser(pydantic_object=TestResults)

prompt_final = PromptTemplate(
    template=prompt,
    input_variables=["objective", "summary", "conditions"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

model = OllamaLLM(model='mistral:latest')

chain = prompt_final | model | parser

ans = chain.invoke({'objective': objective, 'summary': summary, 'conditions': conditions})
