import pandas as pd
from tqdm.auto import tqdm
from utils import connect_to_llm
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import configs.general.config as c
import random


sub = pd.read_csv(c.subjects_path)
programs = pd.read_csv(c.programs_path)
programs = programs[programs['תת סל'].isin(sub.Name.unique())].sample(20, random_state=42).reset_index()

# index = 2

llm = connect_to_llm(endpoint='phi4:latest')
# with open('configs/tests/prompts/team_competency.txt', 'r') as f:
#     prompt = f.read()

prompt = """
```
```
You are a highly analytical program evaluator. You will be provided with information about a program and a set of minimum requirements. Your task is to determine the program's suitability based on these requirements.

**Input:**

* **Central Goal of the Program:** {central_goal}
* **Summary of the Program:** {program_summary}
* **Minimum Requirements for the Subject:** {minimum_requirements}

**Task:**

1.  Analyze the program's central goal and summary.
2.  Compare the program's features and objectives to the list of minimum requirements.
3.  Assign a score from 1 to 5, where:
    * 1 - Not suitable
    * 2 - Slightly suitable
    * 3 - Suitable
    * 4 - Very suitable
    * 5 - Perfectly suitable
4.  Provide a clear and concise explanation of how you arrived at the score.

**Output Format (JSON), and make sure it's valid:**

```json
{{
  "Score": <score>,
  "Explanation": "<explanation>"
}}
```

**Begin Evaluation:**
```
"""

final_prompt = PromptTemplate.from_template(prompt)

chain = final_prompt | llm | JsonOutputParser()

test_list = []
random.seed(42)
rand_list = random.sample(range(programs.shape[0]), 5)
print(rand_list)
for i in tqdm(rand_list, position=0, leave=True):
    objective = programs.loc[i, 'מטרה מרכזית']
    summary = programs.loc[i, 'תקציר תוכנית']
    conditions = sub.loc[programs.loc[i, 'תת סל'] == sub['Name'], 'Min_conditions'].values[0]

    args = {
        'central_goal': objective,
        'program_summary': summary,
        'minimum_requirements': conditions
    }
    ans = chain.invoke(args)
    test_list.append({int(programs.loc[i, 'index']): ans})

# chain_raw = final_prompt | llm
# ans_raw = chain_raw.invoke(args)
