import os
import logging
import subprocess

# -------------------------- General --------------------------- #
_local_path = os.getcwd()
valid_tests_type = ['educational_goals', 'sub_sal']  # valid test type
running_tests_type = 'educational_goals'  # current running test type
running_tests = 'all'  # all tests for examine, type 'all' to examine all possible test

# ---------------------------- Log ----------------------------- #
logger = logging.getLogger()
log_level = logging.INFO
logger.setLevel(log_level)

# --------------------------- Tests ---------------------------- #
sub_sal_valid_tests = ['team_competency', 'content', 'keywords', 'goals']  # all 'sub_sal' possible tests
educational_goals_valid_tests = ['content', 'context', 'success_measures']  # all 'educational_goals' possible tests
valid_tests = sub_sal_valid_tests if running_tests_type == 'sub_sal' else educational_goals_valid_tests  # set the valid tests for this running

# ---------------------------- Data ---------------------------- #
programs_limit = 10  # limit number of programs to examine, type None i no limit needed
remove_exists = False  # if 'True' will remove all programs that already examined
examination_subset = ['program_number', 'tat_sal'] if running_tests_type == 'sub_sal' else ['program_number']  # columns to drop duplicates by
program_subset = ['מספר תוכנית', 'תת סל'] if running_tests_type == 'sub_sal' else ['מספר תוכנית']  # columns to drop program duplicates by
sub_sal_path = os.path.join(_local_path, os.path.abspath(r'data/source/sub_sal/sub_sal_approved_with_tables.csv'))  # 'sub_sal' data source
educational_goals_path = os.path.join(_local_path, os.path.abspath(r'data/source/educational_goals/goals_texts'))  # educational_goals data source
programs_path = os.path.join(_local_path, os.path.abspath(r'data/source/general/gefen_programs_limited_data.csv'))  # programs data source

# ---------------------------- LLM ----------------------------- #
endpoint = 'azure'
# ollama_models = [i.split()[0] for i in subprocess.check_output(['ollama', 'list']).decode('utf-8').split('\n')[1:] if i]

# ------------------------- Tests path -------------------------- #
yaml = os.path.join(_local_path, os.path.abspath(fr'configs/tests/{running_tests_type}/yaml_configs'))  # directory of YAML files
prompts = os.path.join(_local_path,os.path.abspath(fr'configs/tests/{running_tests_type}/prompts'))  # directory of prompts files

# --------------------------- Output ---------------------------- #
drop_iteration = 5  # drop data every X iteration
final_results = os.path.join(_local_path, os.path.abspath(f'data/output/{running_tests_type}/final/final_results.csv'))  # directory of final_results file
errors = os.path.join(_local_path, os.path.abspath(fr'data/output/{running_tests_type}/errors'))  # directory of errors files
