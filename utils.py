import os
import yaml
import pandas as pd
from typing import Literal
import configs.general.config as c
from dotenv import load_dotenv, find_dotenv
from langchain_ollama.llms import OllamaLLM
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

load_dotenv(find_dotenv())


def validate_tests():
    """
    A validation that the user enter correctly the tests parameter before the progress start
    """
    # test type validator
    if c.running_tests_type not in c.valid_tests_type:
        c.rootLogger.critical(f"'{c.running_tests_type}' is not a valid test. Please choose from {c.valid_tests_type}")
        exit()

    # tests validator in case of wrong name or not exist test
    if isinstance(c.running_tests, list):
        not_valid_tests = [test for test in c.running_tests if test not in c.valid_tests]

        if not_valid_tests:
            c.rootLogger.critical(f"{not_valid_tests} not a valid test. Please choose from {c.valid_tests}")
            exit()

    # test validator in case of wrong 'all' option
    if isinstance(c.running_tests, str) and c.running_tests.lower() != 'all':
        c.rootLogger.error(f"'{c.running_tests}' not a valid option. Please try 'all' to run al valid tests possible")
        exit()


def drop_exist(df: pd.DataFrame):
    """
    Drop exists records from program df
    Args:
        df (pd.DataFrame): A dataframe with all the records we want to reduce records that already exists in the final answers file

    Returns:
        The same dataframe with all the records that not processed yet
    """
    # read the 'final_results' csv
    drop_from = pd.read_csv(c.final_results) if c.final_results.endswith('.csv') else pd.read_excel(c.final_results)

    # get the index of rows in `program_df` that should be dropped
    indices_to_drop = df.merge(drop_from, left_on=c.program_subset, right_on=c.examination_subset, how='inner').index

    # drop those rows from `program_df`
    df = df.drop(indices_to_drop)
    c.rootLogger.info(f"successfully removed {len(indices_to_drop)} exists records from 'programs data'")

    return df


def append_general_data_to_row(row: pd.Series) -> dict:
    """
    Add the program general data to the llm answer dictionary
    Args:
        row (pd.Series): The specific program row from the programs df

    Returns:
        The program general information in a dictionary form
    """
    general_dict = {
        'program_number': row['מספר תוכנית'],
        'organization_name': row['שם ארגון'],
        'program_name': row['שם תוכנית'],
        'main_target': row['מטרה מרכזית'],
        'description': row['תקציר תוכנית'],
    }

    if c.running_tests_type == 'sub_sal':
        general_dict['tat_sal'] = row['תת סל']

    return general_dict


def drop_data(drop_df: pd.DataFrame):
    """
    Drop the programs that invoked by the LLM to the final_answer dataframe
    Args:
        drop_df (pd.DataFrame): programs complete rows as dataframe
    """
    # convert data that collected through current iteration into df
    drop_num = len(drop_df)

    # check if 'final_results' is already exist, read this csv file and drop duplicates if exist
    if os.path.isfile(c.final_results):
        exist_temp_df = pd.read_csv(c.final_results)
        drop_df = pd.concat([exist_temp_df, drop_df]).reset_index(drop=True).drop_duplicates(subset=c.examination_subset, keep='last')

    try:
        drop_df.to_csv(c.final_results, index=False, encoding='utf-8-sig')
        c.rootLogger.info(f"successfully dropped {drop_num} analyzed programs")

    except Exception as e:
        c.rootLogger.exception(f"Failed to drop {drop_num} analyzed programs: {e}")


def ask_llm(test_dict: dict, programs_df: pd.DataFrame, examination_data: pd.DataFrame = None, llm=None) -> pd.DataFrame:
    """
    Aggregate essential information using the test dictionary and invoke the LLM
    Args:
        test_dict (dict): A dictionary with all the essential information that this test needs to be able to invoke the LLM
        programs_df (pd.DataFrame): The program df
        examination_data (pd.DataFrame): The examination information. If None, the information should be store within the test dictionary
        llm: the llm object that was created once.

    Returns:
        A dictionary with the LLM answer contain the score, the justification and more keys if needed
    """
    if llm is None:
        raise ValueError("LLM object must be provided.")

    general_data_list = []
    batch = []
    batches = []
    for index, row in programs_df.iterrows():
        examination = examination_data[examination_data['Name'] == row['תת סל']] if c.running_tests_type == 'sub_sal' else None
        program_params = {k: row[v] for k, v in test_dict['program_params'].items()} if test_dict['program_params'] else {}
        examination_params = {}
        if test_dict['examination_params']:
            if c.running_tests_type == 'sub_sal':
                examination_params = {k: examination[v] for k, v in test_dict['examination_params'].items()}
            elif c.running_tests_type == 'educational_goals':
                examination_params = {test_dict['examination_params']['param']: test_dict['examination_params']['goals_file']}
        prompt_params = {**program_params, **examination_params}
        batch.append({k: v for k, v in prompt_params.items()})
        general_data_list.append(append_general_data_to_row(row=row))
        if (int(index)+1) % c.batch_size == 0:
            batches.append((batch, general_data_list))
            batch = []
            general_data_list = []
    if batch:
        batches.append((batch, general_data_list))
    final_prompt = PromptTemplate.from_template(template=test_dict['prompt'])
    chain = final_prompt | llm | JsonOutputParser()

    try:
        df_list = []
        for b, general in batches:
            ans = chain.batch(b)
            ans = [{f"{test_dict['name']}_{k}": v for k, v in a.items()} for a in ans]
            general_data_and_ans_list = [{**g, **a} for g, a in zip(general, ans)]
            df_list.extend(general_data_and_ans_list)
        final_df = pd.DataFrame(df_list)
        return final_df
    except Exception as e:
        print(e)


def create_tests_dict(test_name: str, test_type: str) -> dict:
    """
    Create the test dictionary out of the YAML file
    Args:
        test_name (str): The name of the test
        test_type (str): The type of the test ('educational_goals' | 'sub_sal')

    Returns:
        A dictionary with all the essential information that this test needs to be able to invoke the LLM
    """
    # read the test YAML file
    try:
        with open(os.path.join(c.yaml, f'{test_name}.yaml'), 'r', encoding='utf-8-sig') as file:
            total_dict = yaml.safe_load(file)

    except Exception as e:
        c.rootLogger.exception(e)

    # read the test prompt
    try:
        with open(os.path.join(c.prompts, total_dict['prompt']), 'r', encoding="utf-8-sig") as p_file:
            total_dict['prompt'] = p_file.read()

    except Exception as e:
        c.rootLogger.exception(e)

    # 'educational_goals' examination parameters are in text file and not csv
    if test_type == 'educational_goals':
        try:
            with open(os.path.join(c.educational_goals_path, total_dict['examination_params']['goals_file']), 'r', encoding='utf-8-sig') as p_file:
                total_dict['examination_params']['goals_file'] = p_file.read()

        except Exception as e:
            c.rootLogger.exception(e)

    total_dict['name'] = test_name

    return total_dict


def connect_to_llm(endpoint: str = Literal["google", "azure"],
                   temp: float = 0.) -> AzureChatOpenAI | ChatGoogleGenerativeAI:
    """
    Connect to a LLM model (Ollama's model) or LLM endpoint ('azure' | 'google')
    Args:
        endpoint (str): The model endpoint (options = 'azure' | 'google')
        temp (float): The model temperature (default = 0.0)

    Returns:
        The LLM model or endpoint
    """
    if endpoint == 'azure':
        try:
            chat_llm = AzureChatOpenAI(
                # openai_api_version=os.getenv('OPENAI_API_VERSION'),
                # openai_api_key=os.getenv('OPENAI_API_KEY'),
                azure_endpoint=os.getenv('OPENAI_API_BASE'),
                openai_api_type=os.getenv('OPENAI_API_TYPE'),
                model=os.getenv('MODEL_NAME'),
                temperature=temp
            )
            c.rootLogger.info('successfully connected to LLM')
            return chat_llm

        except Exception as e:
            c.rootLogger.exception(e)

    elif endpoint == 'google':
        try:
            chat_llm = ChatGoogleGenerativeAI(
                # google_api_key=os.getenv('GEMINI_API_KEY'),
                model="gemini-1.5-pro",
                temperature=temp
            )
            return chat_llm

        except Exception as e:
            c.rootLogger.exception(e)

    # elif endpoint in c.ollama_models:
    #     return OllamaLLM(model=endpoint)

    else:
        c.rootLogger.critical(f"'{endpoint}' is not a valid llm, Please choose 'google', 'azure' or ollama model from this list: {c.ollama_models}")
        exit()


# llm = connect_to_llm(endpoint=c.endpoint)
# llm = OllamaLLM(model='llama3.1:8b')
