import prompts
import utils
import pandas as pd
import configs.general.config as c
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


sub_sal_approved = pd.read_csv(c.subjects_path)
llm = GefenAiTest.connect_to_llm(endpoint='azure')

content_prompt = PromptTemplate.from_template(template=prompts.ExtractKeyWords)
llm_chain = content_prompt | llm | JsonOutputParser()

sub_sal_approved[['mandatory_keywords', 'keywords']] = sub_sal_approved.Description.apply(lambda x: pd.Series(llm_chain.invoke({'description': x})))

sub_sal_approved.to_csv(c.subjects_path, index=False, encoding='utf-8-sig')
