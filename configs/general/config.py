import os
import logging
import subprocess

# -------------------------- General --------------------------- #
_local_path = os.getcwd()
valid_tests = ['educational_goals', 'sub_sal']
running_tests_type = 'educational_goals'
running_tests = 'all'

# ---------------------------- Log ----------------------------- #
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ----------------------- Sub-sal Tests ------------------------ #
sub_sal_valid_tests = ['team_competency', 'content', 'keywords', 'goals']

# ------------------ Educational goals Tests ------------------- #
educational_goals_valid_tests = ['content', 'context', 'success_measures']

# ---------------------------- Data ---------------------------- #
row_limit = 3
remove_drops = True
sub_sal_path = os.path.join(_local_path, os.path.abspath(r'data/source/sub_sal/sub_sal_approved_with_tables.csv'))
educational_goals_path = os.path.join(_local_path, os.path.abspath(r'data/source/educational_goals/goals_texts'))
programs_path = os.path.join(_local_path, os.path.abspath(r'data/source/general/gefen_programs_limited_data.csv'))

# ---------------------------- LLM ----------------------------- #
endpoint = 'google'
# ollama_models = [i.split()[0] for i in subprocess.check_output(['ollama', 'list']).decode('utf-8').split('\n')[1:] if i]

# ------------------------- Tests path -------------------------- #
yaml = os.path.join(_local_path, os.path.abspath(fr'configs/tests/{running_tests_type}/yaml_configs'))
prompts = os.path.join(_local_path,os.path.abspath(fr'configs/tests/{running_tests_type}/prompts'))

# --------------------------- Output ---------------------------- #
drop_iteration = 2
subset = ['program_number', 'tat_sal'] if running_tests_type == 'sub_sal' else ['program_number']
final_results = os.path.join(_local_path, os.path.abspath(f'data/output/{running_tests_type}/final/final_results.csv'))
errors = os.path.join(_local_path, os.path.abspath(fr'data/output/{running_tests_type}/errors'))
