import os
import utils
import pandas as pd
from time import sleep
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
    if isinstance(c.running_tests, str) and c.running_tests.lower() == 'all':
        c.running_tests = c.valid_tests
    tests_dict_list = [utils.create_tests_dict(test_name=test, test_type=c.running_tests_type) for test in c.running_tests]

    # in case the user want to limit the number of programs that analyzed by the llm
    if c.programs_limit and c.programs_limit < len(programs_df):
        programs_df = programs_df.sample(c.programs_limit, random_state=1).reset_index(drop=True)
        c.rootLogger.info(f'successfully reduce number of programs to {c.programs_limit}')

    chunks = [programs_df[i:i + c.drop_iteration] for i in range(0, len(programs_df), c.drop_iteration)]
    for chunk in tqdm(chunks, leave=True, position=0):
        # if there is more than one test to examine, there is a split into multiprocess for parallel analyzing
        if len(tests_dict_list) > 1:
            new_list = [(x, chunk) for x in tests_dict_list] if c.running_tests_type == 'educational_goals' else [(x, chunk, examination_df) for x in tests_dict_list]
            with Pool(processes=min(cpu_count() - 3, len(tests_dict_list))) as pool:
                c.rootLogger.info(f'split into {pool._processes} processes')
                results = pool.starmap(utils.ask_llm, new_list)
                result = results[0]
                merge_on = list(result.columns[:-2])
                for df in results[1:]:
                    results = pd.merge(result, df, on=merge_on, how='outer')

        # project analysis through specific test
        else:
            results = utils.ask_llm(test_dict=tests_dict_list[0], programs_df=chunk, examination_data=examination_df)

        sleep(1)

        utils.drop_data(drop_df=results)


if __name__ == '__main__':
    utils.validate_tests()  # validate that the test type and tests name is valid
    c.rootLogger.info(f"Running {c.running_tests} tests of type: '{c.running_tests_type}'")

    program_df = pd.read_csv(c.programs_path) if c.programs_path.endswith('.csv') else pd.read_excel(c.programs_path)  # programs df
    c.rootLogger.info(f"successfully load {program_df.shape[0]} programs from 'programs data'")

    if c.remove_exists and os.path.isfile(c.final_results):  # remove all the data that already processed and located in the 'final_results' csv file
        program_df = utils.drop_exist(df=program_df)

    if c.running_tests_type == 'educational_goals':
        program_df = program_df.drop_duplicates(subset=c.program_subset)
        c.rootLogger.info(f'there are {program_df.shape[0]} unique programs to analyze')

    # 'sab_sal' tests type load csv with all the 'tat sal' information
    examination_data = None
    if c.running_tests_type == 'sub_sal':
        examination_data = pd.read_csv(c.sub_sal_path) if c.sub_sal_path.endswith('.csv') else pd.read_excel(c.sub_sal_path)
        c.rootLogger.info(f"successfully load {examination_data.shape[0]} 'tat sal' from 'tat_sal' data'")

    aggregate_batch_results_to_df(
        examination_df=examination_data,
        programs_df=program_df
    )

    c.rootLogger.info('successfully completed all tests')
