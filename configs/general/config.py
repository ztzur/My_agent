import os
import subprocess


_local_path = os.getcwd()
# ------------------------ Gefen Tests ------------------------- #
valid_tests = ['team_competency', 'content', 'correlation', 'keywords', 'goals']
run_tests = ['team_competency', 'content', 'keywords', 'goals']

# ---------------------------- Data ---------------------------- #
subjects_path = os.path.join(_local_path, os.path.abspath('data/sub_sal_approved_with_tables.csv'))
programs_path = os.path.join(_local_path, os.path.abspath('data/gefen_programs_limited_data.csv'))
final_results = os.path.join(_local_path, os.path.abspath('data/outputs/final/final_results.csv'))
drop_iteration = 10
row_limit = 3
remove_drops = None

# ---------------------------- LLM ----------------------------- #
endpoint = 'google'
ollama_models = [i.split()[0] for i in subprocess.check_output(['ollama', 'list']).decode('utf-8').split('\n')[1:] if i]

# ---------------------------- Path ----------------------------- #
yaml = os.path.join(_local_path, os.path.abspath('configs/tests/yaml_configs'))
prompts = os.path.join(_local_path, os.path.abspath('configs/tests/prompts'))
errors = os.path.join(_local_path, os.path.abspath('data/outputs/errors'))
