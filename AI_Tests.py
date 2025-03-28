import os
import pandas as pd
from typing import List
from tqdm.auto import tqdm
import configs.general.config as c
from multiprocessing import Pool, cpu_count
from utils import ask_llm, create_tests_dict


def append_general_data_to_row(row: pd.Series, llm_answer: List[dict]) -> dict:
    general_dict = {
        'program_number': row['מספר תוכנית'],
        'organization_name': row['שם ארגון'],
        'program_name': row['שם תוכנית'],
        'main_target': row['מטרה מרכזית'],
        'description': row['תקציר תוכנית'],
    }

    if c.running_tests_type == 'sub_sal':
        general_dict['tat_sal'] = row['תת סל']

    llm_answer.insert(0, general_dict)
    final_row = {k: v for x in llm_answer for k, v in x.items()}

    return final_row


def drop_data(df_list: List[dict]):
    drop_df = pd.DataFrame(df_list)

    if os.path.isfile(c.final_results):
        exist_temp_df = pd.read_csv(c.final_results)
        drop_df = pd.concat([exist_temp_df, drop_df]).reset_index(drop=True).drop_duplicates(subset=c.subset, keep='last')

    drop_df.to_csv(c.final_results, index=False, encoding='utf-8-sig')


def aggregate_batch_results_to_df(examination_df: pd.DataFrame, programs_df: pd.DataFrame, tests_list: str | List[str], limit_rows: int = None):
    if isinstance(tests_list, str) and tests_list.lower() == 'all':
        tests_list = c.sub_sal_valid_tests if c.running_tests_type == 'sub_sal' else c.educational_goals_valid_tests
    tests_dict_list = [create_tests_dict(test_name=test, test_type=c.running_tests_type) for test in tests_list]
    df_list = []
    rows_counter = 0
    if limit_rows and limit_rows < len(programs_df):
        programs_df = programs_df.sample(limit_rows, random_state=1).reset_index(drop=True)
    for index, row in tqdm(programs_df.iterrows(), total=programs_df.shape[0], leave=False, position=0, desc='Programs'):
        examination = examination_df[examination_df['Name'] == row['תת סל']] if c.running_tests_type == 'sub_sal' else None
        if len(tests_dict_list) > 1:
            new_list = [(x, row) for x in tests_dict_list] if c.running_tests_type == 'educational_goals' else [(x, row, examination) for x in tests_dict_list]
            with Pool(processes=min(cpu_count() - 3, len(tests_dict_list))) as pool:
                results = pool.starmap(ask_llm, new_list)
        else:
            results = [ask_llm(test_dict=tests_dict_list[0], program_row=row, examination_data=examination)]

        df_list.append(append_general_data_to_row(row=row, llm_answer=results))

        if (c.drop_iteration and len(df_list) % c.drop_iteration == 0) or rows_counter + len(df_list) == programs_df.shape[0]:
            drop_data(df_list=df_list)
            rows_counter += c.drop_iteration
            df_list = []


if __name__ == '__main__':
    if c.running_tests_type not in c.valid_tests:
        raise TypeError(f'{c.running_tests_type} is not a valid test\nPlease choose from {c.valid_tests}')

    program_df = pd.read_csv(c.programs_path) if c.programs_path.endswith('.csv') else pd.read_excel(c.programs_path)
    if c.remove_drops and os.path.isfile(c.final_results):
        drop_from = pd.read_csv(c.final_results) if c.final_results.endswith('.csv') else pd.read_excel(c.final_results)

        # Get the index of rows in `program_df` that should be dropped
        left_on = ['מספר תוכנית', 'תת סל'] if c.running_tests_type == 'sub_sal' else ['מספר תוכנית']
        indices_to_drop = program_df.merge(drop_from, left_on=left_on, right_on=c.subset, how='inner').index

        # Drop those rows from `program_df`
        program_df = program_df.drop(indices_to_drop)

    examination_data = None
    if c.running_tests_type == 'sub_sal':
        examination_data = pd.read_csv(c.sub_sal_path) if c.sub_sal_path.endswith('.csv') else pd.read_excel(c.sub_sal_path)

    limit = c.row_limit
    aggregate_batch_results_to_df(
        examination_df=examination_data,
        programs_df=program_df,
        tests_list=c.running_tests,
        limit_rows=limit
    )

    # df.to_csv(c.dump_df, index=False, encoding='utf-8-sig')
