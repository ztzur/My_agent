import os
import yaml
import pandas as pd
import langchain_core
from typing import Literal, List
import configs.general.config as c
from dotenv import load_dotenv, find_dotenv
from langchain_ollama.llms import OllamaLLM
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

load_dotenv(find_dotenv())


def ask_llm(test_dict: dict, program_row: pd.Series, examination_data: pd.Series = None) -> dict:
    program_params = {k: program_row[v] for k, v in test_dict['program_params'].items()} if test_dict['program_params'] else {}

    examination_params = {}
    if test_dict['examination_params']:
        if c.running_tests_type == 'sub_sal':
            examination_params = {k: examination_data[v] for k, v in test_dict['examination_params'].items()}
        elif c.running_tests_type == 'educational_goals':
            examination_params = {test_dict['examination_params']['param']: test_dict['examination_params']['goals_file']}

    prompt_params = {**program_params, **examination_params}
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
            with open(f"{c.errors}/{program_row['מספר תוכנית']}_{program_row['תת סל']}", 'w') as f:
                f.write(f"test: {test_dict['name']}\nprogram_name: {program_row['שם תוכנית']}\nsub subject: {program_row['תת סל']}")
            return {}

    ans_plus_names = {f"{test_dict['name']}_{k}": v for k, v in ans.items()}

    return ans_plus_names


def create_tests_dict(test_name: str, test_type: str) -> dict:
    valid_tests = c.sub_sal_valid_tests if test_type == 'sub_sal' else c.educational_goals_valid_tests
    if test_name not in valid_tests:
        raise TypeError(
            f"'{test_name}' is not a valid test\nPlease choose from {valid_tests}")

    with open(os.path.join(c.yaml, f'{test_name}.yaml'), 'r', encoding='utf-8-sig') as file:
        total_dict = yaml.safe_load(file)

    with open(os.path.join(c.prompts, total_dict['prompt']), 'r', encoding="utf-8-sig") as p_file:
        total_dict['prompt'] = p_file.read()

    if test_type == 'educational_goals':
        with open(os.path.join(c.educational_goals_path, total_dict['examination_params']['goals_file']), 'r', encoding='utf-8-sig') as p_file:
            total_dict['examination_params']['goals_file'] = p_file.read()

    total_dict['name'] = test_name

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

        return chat_llm

    elif endpoint == 'google':
        chat_llm = ChatGoogleGenerativeAI(
            google_api_key=os.getenv('GEMINI_API_KEY'),
            model="gemini-1.5-pro",
            temperature=temp
        )

        return chat_llm

    # elif endpoint in c.ollama_models:
    #     return OllamaLLM(model=endpoint)

    else:
        raise TypeError(
            f"'{endpoint}' is not a valid llm\nPlease choose 'google', 'azure' or ollama model from this list: {c.ollama_models}")


llm = connect_to_llm(endpoint=c.endpoint)
# llm = OllamaLLM(model='llama3.1:8b')
