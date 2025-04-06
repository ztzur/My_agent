import os
import threading

import utils
import pandas as pd
from time import sleep
from tqdm.auto import tqdm
import configs.general.config as c
from multiprocessing import Pool, cpu_count, current_process
from tqdm.contrib.concurrent import process_map  # Import process_map


def ask_llm_worker(test_dict, chunk, examination_df=None):
    """Worker process function to process data with the initialized LLM."""
    process = current_process()
    if 'llm' not in process._kwargs:
        process._kwargs['llm'] = utils.connect_to_llm(endpoint=c.endpoint)
        if process._kwargs['llm'] is None:
            c.rootLogger.critical("Failed to establish LLM connection in worker process.")
            return pd.DataFrame()
    return utils.ask_llm(test_dict=test_dict, programs_df=chunk, examination_data=examination_df, llm=process._kwargs['llm'])


# Create a top-level function to wrap ask_llm_worker
def worker_wrapper(args):
    return ask_llm_worker(*args)


def aggregate_batch_results_to_df(examination_df: pd.DataFrame | None, programs_df: pd.DataFrame):
    """
    Loop over all the programs and simultaneously send all the information for the LLM to do the tests
    Args:
        examination_df (pd.DataFrame | None): The information in the context of which the plan is being examined. If None, the information should be in yaml and text files.
        programs_df (pd.DataFrame): The programs dataframe
    """
    if isinstance(c.running_tests, str) and c.running_tests.lower() == 'all':
        c.running_tests = c.valid_tests
    tests_dict_list = [utils.create_tests_dict(test_name=test, test_type=c.running_tests_type) for test in
                       c.running_tests]

    if c.programs_limit and c.programs_limit < len(programs_df):
        programs_df = programs_df.sample(c.programs_limit, random_state=1).reset_index(drop=True)
        c.rootLogger.info(f'successfully reduce number of programs to {c.programs_limit}')

    chunks = [programs_df[i:i + c.drop_iteration] for i in range(0, len(programs_df), c.drop_iteration)]
    processes = min(cpu_count() - 3, len(tests_dict_list))
    c.rootLogger.info(f'split into {processes} processes')

    for chunk in tqdm(chunks, leave=True, position=0):
        if len(tests_dict_list) > 1:
            new_list = [(x, chunk) for x in tests_dict_list] if c.running_tests_type == 'educational_goals' else [
                (x, chunk, examination_df) for x in tests_dict_list]

            # Use the top-level worker_wrapper function
            results = process_map(worker_wrapper, new_list, max_workers=processes, chunksize=1)

            result = results[0]
            merge_on = list(result.columns[:-2])
            for df in results[1:]:
                results = pd.merge(result, df, on=merge_on, how='outer')
        else:
            results = process_map(ask_llm_worker, [(tests_dict_list[0], chunk, examination_df)], max_workers=processes, chunksize=1)[0]

        sleep(1)
        utils.drop_data(drop_df=results)


if __name__ == '__main__':
    utils.validate_tests()
    c.rootLogger.info(f"Running {c.running_tests} tests of type: '{c.running_tests_type}'")

    program_df = pd.read_csv(c.programs_path) if c.programs_path.endswith('.csv') else pd.read_excel(c.programs_path)
    c.rootLogger.info(f"successfully load {program_df.shape[0]} programs from 'programs data'")

    if c.remove_exists and os.path.isfile(c.final_results):
        program_df = utils.drop_exist(df=program_df)

    if c.running_tests_type == 'educational_goals':
        program_df = program_df.drop_duplicates(subset=c.program_subset)
        c.rootLogger.info(f'there are {program_df.shape[0]} unique programs to analyze')

    examination_data = None
    if c.running_tests_type == 'sub_sal':
        examination_data = pd.read_csv(c.sub_sal_path) if c.sub_sal_path.endswith('.csv') else pd.read_excel(c.sub_sal_path)
        c.rootLogger.info(f"successfully load {examination_data.shape[0]} 'tat sal' from 'tat_sal' data'")

    aggregate_batch_results_to_df(
        examination_df=examination_data,
        programs_df=program_df
    )

    c.rootLogger.info('successfully completed all tests')