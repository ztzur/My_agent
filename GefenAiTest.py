import os

import langchain_core
import yaml
import pandas as pd
from typing import Literal, List

from langchain_core.exceptions import OutputParserException

import configs.general.config as c
from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

load_dotenv(find_dotenv())


def correlation_special_params(program_df: pd.Series, i: int) -> List[dict]:
    df = program_df[program_df['תת סל'] == program_df.loc[i, 'תת סל']]
    correlation_special = [{'Related_Sub_Plan_Objective': obj, 'Related_Sub_Plan_Summary': summary} for obj, summary in zip(df['מטרה מרכזית'], df['תקציר תוכנית'])]
    this_row = {'Related_Sub_Plan_Objective': program_df.loc[i, 'מטרה מרכזית'], 'Related_Sub_Plan_Summary': program_df.loc[i, 'תקציר תוכנית']}
    correlation_special.remove(this_row)

    return correlation_special


def ask_llm(test_name, index, program_df, sub_subject) -> dict:
    # test_name, index, program_df, sub_subject = test_tuple
    test_dict = create_tests_dict(test=test_name)
    program_row = program_df.iloc[index]
    program_params = {k: program_row[v] for k, v in test_dict['program_params'].items()} if test_dict['program_params'] else {}
    subject_params = {k: sub_subject[v] for k, v in test_dict['subject_params'].items()} if test_dict['subject_params'] else {}
    prompt_params = {**program_params, **subject_params}

    if test_dict['special_params']:
        special_params = {test_dict['special_params']['param']: globals().get(test_dict['special_params']['func'])(**{k: locals().get(v) for k, v in test_dict['special_params']['args'].items()})}
        prompt_params = {**prompt_params, **special_params}

    final_prompt = PromptTemplate.from_template(template=test_dict['prompt'])
    chain = final_prompt | llm | JsonOutputParser()
    try:
        ans = chain.invoke({k: v for k, v in prompt_params.items()})
    except OutputParserException as e:
        try:
            temp_prompt_template = test_dict['prompt'] + '\nMake sure that output format is valid!!!'
            temp_prompt = PromptTemplate.from_template(template=temp_prompt_template)
            temp_chain = temp_prompt | llm | JsonOutputParser()
            ans = temp_chain.invoke({k: v for k, v in prompt_params.items()})
        except OutputParserException as e:
            with open(f'{program_row['מספר תוכנית']}_{program_row['תת סל']}', 'w') as f:
                f.write(f'test: {test_name}\nprogram_name: {program_row['שם תוכנית']}\nsub subject: {program_row['תת סל']}')
            return {}

    ans_plus_names = {f'{test_name}_{k}': v for k, v in ans.items()}

    return ans_plus_names


def create_tests_dict(test: str) -> dict:
    if test not in c.valid_tests:
        raise TypeError(
            f"'{test}' is not a valid test\nPlease choose from {c.valid_tests}")

    with open(f'configs/yaml_configs/{test}.yaml', 'r', encoding='utf-8-sig') as file:
        total_dict = yaml.safe_load(file)

    with open(total_dict['prompt'], 'r') as p_file:
        total_dict['prompt'] = p_file.read()

    return total_dict


def connect_to_llm(endpoint: str = Literal["google", "azure"],
                   temp: float = 0.) -> AzureChatOpenAI | ChatGoogleGenerativeAI:
    if endpoint == 'azure':
        chat_llm = AzureChatOpenAI(
            openai_api_version=os.getenv('OPENAI_API_VERSION'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            azure_endpoint=os.getenv('OPENAI_API_BASE'),
            openai_api_type=os.getenv('OPENAI_API_TYPE'),
            model=os.getenv('MODEL_NAME'),
            temperature=temp
        )

    elif endpoint == 'google':
        chat_llm = ChatGoogleGenerativeAI(
            google_api_key=os.getenv('GEMINI_API_KEY'),
            model="gemini-1.5-pro",
            temperature=temp
        )

    return chat_llm


llm = connect_to_llm(endpoint=c.endpoint)
