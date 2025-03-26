import os
import pandas as pd
from tqdm import tqdm
from typing import List
from utils import ask_llm
import configs.general.config as c
from multiprocessing import Pool, cpu_count


def aggregate_batch_results_to_df(subjects_df: pd.DataFrame, programs_df: pd.DataFrame, tests_list: str | List[str], limit_rows: int = None) -> pd.DataFrame:
    if isinstance(tests_list, str) and tests_list.lower() == 'all':
        tests_list = c.valid_tests
    df_list = []
    for _, sub_subject in tqdm(subjects_df.iterrows(), total=subjects_df.shape[0], leave=False, position=0, desc='Sub subjects'):
        sub_program_planes = programs_df[programs_df['תת סל'] == sub_subject['Name']].reset_index(drop=True)
        if limit_rows and limit_rows < len(sub_program_planes):
            sub_program_planes = sub_program_planes.sample(limit_rows, random_state=1).reset_index(drop=True)
        for index, row in tqdm(sub_program_planes.iterrows(), total=sub_program_planes.shape[0], leave=False, position=1, desc='Programs'):
            if len(tests_list) > 1:
                new_list = [(x, index, sub_program_planes, sub_subject) for x in tests_list]
                with Pool(processes=min(cpu_count() - 3, len(tests_list))) as pool:
                    results = pool.starmap(ask_llm, new_list)
            else:
                results = [ask_llm(tests_list[0], index, sub_program_planes, sub_subject)]

            row_dict = {
                'program_number': row['מספר תוכנית'],
                'organization_name': row['שם ארגון'],
                'program_name': row['שם תוכנית'],
                'main_target': row['מטרה מרכזית'],
                'description': row['תקציר תוכנית'],
                'tat_sal': row['תת סל']
            }

            results.insert(0, row_dict)
            final_row = {k: v for x in results for k, v in x.items()}

            df_list.append(final_row)

            if c.drop_iteration and len(df_list) % c.drop_iteration == 0:
                temp_df = pd.DataFrame(df_list)

                if os.path.isfile(c.final_results):
                    exist_temp_df = pd.read_csv(c.final_results)
                    temp_df = pd.concat([exist_temp_df, temp_df]).reset_index(drop=True)

                temp_df.to_csv(c.final_results, index=False, encoding='utf-8-sig')

    return pd.DataFrame(df_list)


if __name__ == '__main__':
    subject_df = pd.read_csv(c.subjects_path) if c.subjects_path.endswith('.csv') else pd.read_excel(c.subjects_path)
    program_df = pd.read_csv(c.programs_path) if c.programs_path.endswith('.csv') else pd.read_excel(c.programs_path)
    if c.remove_drops and os.path.isfile(c.final_results):
        drop_from = pd.read_csv(c.final_results) if c.final_results.endswith('.csv') else pd.read_excel(c.final_results)
        drop_from.set_index(['program_number', 'tat_sal'], inplace=True)
        program_df.set_index(['מספר תוכנית', 'תת סל'], inplace=True)

        program_df = program_df.loc[program_df.index.difference(drop_from.index)].reset_index()

    limit = c.row_limit
    df = aggregate_batch_results_to_df(
        subjects_df=subject_df,
        programs_df=program_df,
        tests_list=c.run_tests,
        limit_rows=limit
    )

    # df.to_csv(c.dump_df, index=False, encoding='utf-8-sig')
