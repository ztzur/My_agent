import os
import utils
import pandas as pd
from tqdm.auto import tqdm
import configs.general.config as c
from multiprocessing import Pool, cpu_count


def aggregate_batch_results_to_df(examination_df: pd.DataFrame | None, programs_df: pd.DataFrame):
    """
    Loop over all the programs and simultaneously send all the information for the LLM to do the tests
    Args:
        examination_df (pd.DataFrame | None): The information in the context of which the plan is being examined. If None, the information should be in yaml and text files.
        programs_df (pd.DataFrame): The programs dataframe
    """
    # create a dictionary that store all the information that essential for the llm in order to invoke the program different tests
    if c.running_tests.lower() == 'all':
        c.running_tests = c.valid_tests
    tests_dict_list = [utils.create_tests_dict(test_name=test, test_type=c.running_tests_type) for test in c.running_tests]

    df_list = []
    rows_counter = 0

    # in case the user want to limit the number of programs that analyzed by the llm
    if c.programs_limit and c.programs_limit < len(programs_df):
        programs_df = programs_df.sample(c.programs_limit, random_state=1).reset_index(drop=True)

    # a loop through all the programs
    for index, row in tqdm(programs_df.iterrows(), total=programs_df.shape[0], leave=False, position=0, desc='Programs'):
        # get the information to correlated 'tat_sal' in 'tat_sal' tests type case
        examination = examination_df[examination_df['Name'] == row['תת סל']] if c.running_tests_type == 'sub_sal' else None

        # if there is more than one test to examine, there is a split into multiprocess for parallel analyzing
        if len(tests_dict_list) > 1:
            new_list = [(x, row) for x in tests_dict_list] if c.running_tests_type == 'educational_goals' else [(x, row, examination) for x in tests_dict_list]
            with Pool(processes=min(cpu_count() - 3, len(tests_dict_list))) as pool:
                results = pool.starmap(utils.ask_llm, new_list)
        # project analysis through specific test
        else:
            results = [utils.ask_llm(test_dict=tests_dict_list[0], program_row=row, examination_data=examination)]

        df_list.append(utils.append_general_data_to_row(row=row, llm_answer=results))

        # after each iteration the data been downloaded into 'final_answers' csv in case of a runtime error.
        if (c.drop_iteration and len(df_list) % c.drop_iteration == 0) or rows_counter + len(df_list) == programs_df.shape[0]:
            utils.drop_data(df_list=df_list)
            rows_counter += c.drop_iteration
            df_list = []


if __name__ == '__main__':
    utils.validate_tests()  # validate that the test type and tests name is valid
    program_df = pd.read_csv(c.programs_path) if c.programs_path.endswith('.csv') else pd.read_excel(c.programs_path)  # programs df
    if c.remove_exists and os.path.isfile(c.final_results):  # remove all the data that already processed and located in the 'final_results' csv file
        program_df = utils.drop_exist(df=program_df)

    if c.running_tests_type == 'educational_goals':
        program_df = program_df.drop_duplicates(subset=c.program_subset)

    # 'sab_sal' tests type load csv with all the 'tat sal' information
    examination_data = None
    if c.running_tests_type == 'sub_sal':
        examination_data = pd.read_csv(c.sub_sal_path) if c.sub_sal_path.endswith('.csv') else pd.read_excel(c.sub_sal_path)

    aggregate_batch_results_to_df(
        examination_df=examination_data,
        programs_df=program_df
    )
