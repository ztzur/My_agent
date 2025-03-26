ContentAndContextTest = """"
**Instructions:**

You will be provided with three pieces of information:

1. **Sub-Program Objective:** A concise statement describing what the sub-program aims to achieve.
2. **Sub-Program Summary:** A brief overview of the sub-program, including its key activities and intended outcomes.
3. **Main Program Definition:** A central definition of the overarching program that the sub-program is intended to support. This definition outlines the core purpose and goals of the main program.

Your task is to analyze whether the **Sub-Program Objective** aligns with the **Main Program Definition**. Consider the **Sub-Program Summary** as context to aid your analysis.

**Scoring:**

Assign a score based on the following scale:

* **5 - Perfect Fit:** The Sub-Program Objective is perfectly aligned with the Main Program Definition. The sub-program directly and comprehensively contributes to the core purpose and goals of the main program. The Sub-Program Summary clearly demonstrates this strong alignment.
* **4 - Good Fit:** The Sub-Program Objective aligns well with the Main Program Definition. The sub-program contributes significantly to the main program's goals, although there might be minor areas of less direct alignment or some nuances not fully addressed. The Sub-Program Summary supports this assessment.
* **3 - Partial Fit:** The Sub-Program Objective aligns with some aspects of the Main Program Definition, but not all. There might be areas of misalignment, or the connection is not clearly established. The Sub-Program Summary may highlight some alignment but also suggest potential gaps or areas where the connection could be stronger.
* **2 - Poor Fit:** The Sub-Program Objective has a weak connection to the Main Program Definition. While there might be some tangential relationship, the sub-program does not effectively contribute to the main program's core goals. The Sub-Program Summary will likely reflect this weak connection.
* **1 - No Fit:** The Sub-Program Objective does not align with the Main Program Definition. The sub-program's goals and activities are unrelated or even contradictory to the main program's purpose. The Sub-Program Summary will demonstrate a lack of connection to the main program's goals.

**Output Format:**

Provide your response in the following json format and make sure the json is valid:

```
{{json
    "Score": [Your Score (5, 4, 3, 2, or 1)],
    "Justification": [A concise explanation of your score, referencing specific elements from the Sub-Program Objective, Sub-Program Summary, and Main Program Definition. Explain *why* you chose the score you did, providing evidence for your assessment. Be specific about which aspects align and which do not.]
}}
```

**Example Input:**

```
Sub-Program Objective: To improve the digital literacy skills of senior citizens.
Sub-Program Summary: This sub-program will offer free computer classes to senior citizens, focusing on internet safety, email communication, and basic software applications.
Main Program Definition: To bridge the digital divide and ensure equitable access to technology and digital skills for all citizens.
```

**Example Output:**

```
{{json
    "Score": "5",
    "Justification": "The Sub-Program Objective directly and comprehensively addresses a key component of the Main Program Definition, which is bridging the digital divide by improving digital skills. The Sub-Program Summary further reinforces this alignment by detailing activities that specifically target improving digital skills (computer classes focusing on internet safety, email, and software) for a specific demographic (senior citizens) often affected by the digital divide.  The sub-program is a perfect fit as it directly contributes to the core goal of the main program."
}}
```

**Input Data:**

Sub-Program Objective: {objective}
Sub-Program Summary: {summary}
Main Program Definition: {definition}
"""

KeywordsTest = """
```json
{{
  "score": "[1, 2, 3, 4, or 5]",
  "explanation_hebrew": "[Explanation in Hebrew of how the score was calculated, including the analysis of mandatory and general keywords and their presence/absence in the program goal and description. Be specific about the connections and any gaps or areas for improvement.]"
}}
```

**Instructions:**

You will be provided with the following information:

1.  **Mandatory Keywords:** A list of keywords that are absolutely essential to the program's alignment with a specific goal.
2.  **General Keywords:** A list of additional keywords that are relevant to the program but are not considered mandatory.
3.  **Program Main Goal:** A concise statement describing the primary objective of the program.
4.  **Program General Description:** A brief overview of the program's activities and intended outcomes.

Your task is to analyze the program based on its goal and general description and determine how well it aligns with the provided keywords. You will calculate a weighted score, giving 70% weight to the mandatory keywords and 30% weight to the general keywords.

**Scoring Method:**

1.  **Mandatory Keyword Score:**
    * Determine the degree to which the mandatory keywords are present and relevant in the program goal and description.
    * Assign a score from 1 to 5, where:
        * 1 = Very low alignment
        * 5 = Very high alignment
2.  **General Keyword Score:**
    * Determine the degree to which the general keywords are present and relevant in the program goal and description.
    * Assign a score from 1 to 5, using the same scale as above.
3.  **Weighted Score Calculation:**
    * Calculate the weighted score using the following formula:
        * Weighted Score = (Mandatory Keyword Score * 0.7) + (General Keyword Score * 0.3)
    * Round the weighted score to the nearest whole number (1-5).

**Output Format:**

Return your answer in JSON format exactly as shown above.

* `score`: This field should contain the calculated weighted score (1-5).
* `explanation_hebrew`: This field should contain an explanation in Hebrew of how the score was calculated. This explanation should detail the analysis of both mandatory and general keywords and their presence or absence in the program goal and description.

**Example Input (Illustrative):**

```
Mandatory Keywords: ["מוטיבציה", "תלמידים"]
General Keywords: ["חקר מדעי", "תחרויות מדעיות", "חשיבה ביקורתית"]
Program Main Goal: לעודד תלמידים לחקור מדעים.
Program General Description: התכנית תקיים סדנאות חקר ועידוד השתתפות בתחרויות מדעיות.
```

**Example Output (Illustrative - The actual content would depend on the input):**

```json
{{
  "score": "5",
  "explanation_hebrew": "התוכנית מתאימה מאוד למילות המפתח. מילות החובה 'מוטיבציה' ו'תלמידים' מופיעות באופן ישיר במטרה ובתיאור התוכנית. מילות המפתח הכלליות 'חקר מדעי' ו'תחרויות מדעיות' מופיעות גם הן בתיאור. המילה 'חשיבה ביקורתית' אינה מופיעה ישירות, אך ניתן להסיק שהסדנאות והתחרויות מעודדות חשיבה זו. לכן, מילות החובה קיבלו ציון 5 ומילות המפתח הכלליות קיבלו ציון 5. (5*0.7)+(5*0.3)=5. ציון סופי 5."
}}
```

**Input Data**

Mandatory Keywords: {mandatory_keywords}
General Keywords:  {general_keywords}
Program Main Goal: {program_goal}
Program General Description: {program_description}
"""

TeamCompetencyTest = """
**Instructions:**

You will be provided with three pieces of information:

1. **Sub-Program Objective:** A concise statement describing what the sub-program aims to achieve.
2. **Sub-Program Summary:** A brief overview of the sub-program, including its key activities, resources, and intended outcomes.
3. **Main Program Threshold Conditions:** A list of specific requirements or criteria that *must* be met for a sub-program to be considered aligned with the main program. These conditions often relate to resource allocation, staffing qualifications, target demographics, or other essential elements. They are *necessary* but not necessarily *sufficient* for full alignment.

Your task is to analyze whether the **Sub-Program Objective** and **Sub-Program Summary** describe conditions that satisfy the **Main Program Threshold Conditions**.

**Scoring:**

Assign a score based on the overlap and alignment of the sub-program conditions with the main program's threshold conditions:

* **5 - Identical Requirements:** The Sub-Program Objective and Summary explicitly state conditions that are identical to, or fully encompass, all of the Main Program Threshold Conditions. The sub-program clearly and completely meets all necessary requirements.
* **4 - Most Requirements Overlap:** The Sub-Program Objective and Summary mention conditions that overlap with most (but not all) of the Main Program Threshold Conditions.  There might be minor discrepancies or a few missing details, but the core requirements are addressed.
* **3 - Partially Overlapping Requirements:** The Sub-Program Objective and/or Summary mention conditions that partially overlap with the Main Program Threshold Conditions. Some requirements are met, but others might be missing, less specific, or not fully aligned. There's a degree of compliance, but gaps exist.
* **2 - Few Overlapping Requirements:** The Sub-Program Objective and/or Summary mention conditions that overlap with only a few of the Main Program Threshold Conditions.  Many requirements are not addressed or are significantly different.  The connection to the threshold conditions is weak.
* **1 - Completely Different Requirements:** The Sub-Program Objective and Summary describe conditions that are entirely different from the Main Program Threshold Conditions. There is little to no alignment with the required criteria.

**Output Format:**

Provide your response in the following json format and make sure the json is valid:

```json
{{
    "Score": [Your Score (5, 4, 3, 2, or 1)],
    "Justification": [A concise explanation of your score, referencing specific elements from the Sub-Program Objective, Sub-Program Summary, and Main Program Threshold Conditions. Clearly state which threshold conditions are met, partially met, or not met at all. Explain *why* you chose the score you did, providing evidence for your assessment.  Be specific about which requirements overlap and which do not.]
}}
```

**Example Input:**

```
Sub-Program Objective: To train community health workers in providing mental health first aid.
Sub-Program Summary: This sub-program will offer a 40-hour training course, led by certified instructors, to community health workers. Participants will receive certification upon completion.  The training will cover modules A, B, and C.
Main Program Threshold Conditions:
*   Trainers must be certified in the specific training curriculum.
*   Training must be at least 30 hours in duration.
*   Participants must receive formal certification upon completion of training.
*   The training must cover modules A, B, and C.
```

**Example Output:**

```json
{{
    "Score": "5",
    "Justification": "The Sub-Program Summary clearly states that the training will be led by "certified instructors," fulfilling the first threshold condition. The training duration is specified as "40 hours," exceeding the minimum requirement of "30 hours," thus satisfying the second condition. The summary mentions that participants will "receive certification upon completion," matching the third threshold condition. Finally, the training covering modules A, B, and C fulfills the last threshold condition. Since all threshold conditions are met identically, the score is 5."
}}
```

**Another Example Input:**

```
Sub-Program Objective:  Improve access to educational resources for underprivileged youth.
Sub-Program Summary: This sub-program will provide online tutoring sessions to students in low-income neighborhoods.  Tutors will have some college experience.
Main Program Threshold Conditions:
*   Tutors must have a bachelor's degree in the subject they are tutoring.
*   Tutoring must be provided in person at designated community centers.
*   The program must offer resources in at least three different academic subjects.
```

**Another Example Output:**

```json
{{
    "Score": "2",
    "Justification": "The Sub-Program Summary describes "online tutoring sessions," which does not meet the requirement of "in-person" tutoring at "designated community centers." The requirement of tutors having a "bachelor's degree" is not met by "some college experience." The Sub-Program information doesn't mention the range of subjects covered. Only the general concept of "educational resources" overlaps, but not the specific requirements. Therefore, the score is 2."
```
**Input Data**

Sub-Program Objective: {objective}
Sub-Program Summary: {summary}
Main Program Threshold conditions: {conditions}
"""

GoalsTest = """
**Instructions:**

You will be provided with three pieces of information:

1. **Sub-Program Goal:** A concise statement describing what the sub-program aims to achieve.
2. **Sub-Program Summary:** A brief overview of the sub-program, including its key activities and intended outcomes.
3. **Main Program Definition:** A central definition of the overarching program that the sub-program is intended to support. This definition outlines the core purpose and goals of the main program.

Your task is to analyze the alignment of the Sub-Program Goal and Summary with the Main Program Definition through a two-step process:

**Step 1: Main Program Goal Formulation:**

Based on the provided Main Program Definition, formulate *three distinct goals* of the main program.  These goals should be specific, measurable, achievable, relevant, and time-bound (SMART) where possible, or at least clearly defined and distinguishable from each other.  Express these goals in concise and actionable statements.

**Step 2: Sub-Program Alignment Check:**

Analyze whether the Sub-Program Goal and Summary align with the three goals you formulated in Step 1.  Assess the degree of overlap and identify which of the main program's goals are addressed by the sub-program.

**Scoring:**

Assign a score based on the following scale:

* **5 - Completely Identical Goals:** The Sub-Program Goal and Summary perfectly align with all three of the Main Program Goals you formulated. The sub-program's intended outcomes are completely identical to the desired results of the main program.
* **4 - Mostly Identical Goals:** The Sub-Program Goal and Summary align closely with all three of the Main Program Goals. There might be minor variations in phrasing or scope, but the core objectives are essentially the same.
* **3 - Some Overlapping Goals:** The Sub-Program Goal and Summary align with some (but not all) of the Main Program Goals you formulated.  There is a clear overlap in some areas, but other goals of the main program are not addressed by the sub-program.
* **2 - Few Overlapping Goals:** The Sub-Program Goal and Summary align with only a few of the Main Program Goals. The overlap is limited, and the sub-program addresses only a small portion of the main program's overall objectives.
* **1 - Almost No Overlap:** The Sub-Program Goal and Summary show almost no alignment with the Main Program Goals you formulated. There is minimal overlap, and the sub-program's focus is significantly different from the main program's objectives.

**Output Format:**

Provide your response in the following json format and make sure the json is valid:

```json
{{
    "Main_Program_Goals": [Main program goals (goal 1, goal 2 and goal 3)],
    "Score": [Your Score (5, 4, 3, 2, or 1)],
    "Justification": [A concise explanation of your score, referencing specific elements from the Sub-Program Goal, Sub-Program Summary, and the Main Program Goals you formulated. Clearly state which main program goals are addressed, partially addressed, or not addressed at all by the sub-program. Explain *why* you chose the score you did, providing evidence for your assessment.]
}}
```

**Example Input:**

```
Sub-Program Goal: To improve the digital literacy skills of senior citizens.
Sub-Program Summary: This sub-program will offer free computer classes to senior citizens, focusing on internet safety, email communication, and basic software applications.
Main Program Definition: To bridge the digital divide and ensure equitable access to technology and digital skills for all citizens.
```

**Example Output:**

```json
{{
    "Main_Program_Goals": "To increase access to technology and internet connectivity for underserved communities.", "To enhance digital literacy and skills among all citizens.", "To promote equitable participation in the digital economy.",
    "Score": "4",
    "Justification": "The Sub-Program Goal and Summary strongly align with Main Program Goal 2 (enhancing digital literacy and skills). The computer classes focusing on internet safety, email, and software directly contribute to this goal. While access (Goal 1) is implied by providing the classes, it's not explicitly stated that the sub-program addresses access to technology itself.  Goal 3 (participation in the digital economy) is not directly addressed by the sub-program's activities.  Therefore, while there's strong alignment with one key goal and some implicit connection to another, the sub-program doesn't fully address all three goals, resulting in a score of 4."
}}
```
**Input Data**

Sub-Program Objective: {objective}
Sub-Program Summary: {summary}
Main Program Definition: {definition}
"""

ExtractKeyWords = """
```json
{{
  "mandatory_keywords": "[List of 2-3 mandatory keywords in Hebrew]",
  "additional_keywords": "[List of remaining keywords in Hebrew]"
}}
```

You will be provided with a text in Hebrew containing a Ministry of Education goal, including its objectives, indicators, and a bottom line (שורה תחתונה). Your task is to analyze this text and extract a list of the most relevant keywords and phrases in Hebrew.

**Specifically, you must:**

1.  **Extract Keywords:** Identify the most important keywords and phrases representing the core concepts, goals, and key themes.
2.  **Separate Keywords:** Divide the extracted keywords into two lists:
    * **Mandatory Keywords:** Select 2-3 keywords that are absolutely essential to understanding the core purpose of the goal. These should be the most central and critical terms.
    * **Additional Keywords:** Include all remaining extracted keywords in this list.

**Output Format:**

Return your answer in JSON format exactly as shown above.

* `mandatory_keywords`: This field should contain a list of 2-3 mandatory keywords in Hebrew.
* `additional_keywords`: This field should contain a list of the remaining keywords in Hebrew.

**Example Input (Hebrew):**

```
מטרה: העלאת מוטיבציה בקרב תלמידים לחקר מדעי.
יעדים:
1. הגדלת מספר התלמידים המשתתפים בתחרויות מדעיות.
2. עידוד חשיבה ביקורתית ויצירתית בקרב תלמידים.
מדדים:
1. מספר התלמידים הרשומים לתחרויות מדעיות.
2. איכות הפרויקטים המדעיים המוגשים.
תכלית: טיפוח דור עתיד של מדענים וחוקרים.
```

**Example Output (JSON):**

```json
{{
  "mandatory_keywords": ["מוטיבציה", "חקר מדעי"],
  "additional_keywords": ["תלמידים", "תחרויות מדעיות", "חשיבה ביקורתית", "חשיבה יצירתית", "פרויקטים מדעיים", "מדענים", "חוקרים"]
}}
```

**Now, please provide the text in Hebrew for keyword extraction and separation.**

**Input Data**

Description: {description}
"""

CorrelationTest = """
**Instructions:**

You will be provided with the following information:

1. **Current Sub-Plan Objective:** A concise statement describing what the current sub-plan aims to achieve.
2. **Current Sub-Plan Summary:** A brief overview of the current sub-plan, including its key activities and intended outcomes.
3. **Other Related Sub-Plan Information:** A collection of objectives and summaries for other sub-plans related to the same main plan.  This will be provided as a list, where each item in the list contains:
    *   **Related Sub-Plan Objective:** The objective of the related sub-plan.
    *   **Related Sub-Plan Summary:** A summary of the related sub-plan.

Your task is to analyze the correlation.txt and integration between the *current* sub-plan and the *other* related sub-plans.  Consider how well the current sub-plan's objective and summary align and complement the objectives and summaries of the other sub-plans.

**Scoring:**

Assign a score based on the level of integration:

* **5 - Full Integration:** The current sub-plan is fully integrated with all other related sub-plans.  There is complete alignment and synergy. The objectives and summaries work together seamlessly to achieve a common goal.  There is no redundancy or conflict.
* **4 - Good Integration:** The current sub-plan is well integrated with most other related sub-plans.  There is strong alignment and good synergy.  Minor overlaps or inconsistencies may exist, but they do not significantly detract from the overall integration.
* **3 - Partial Integration:** The current sub-plan is partially integrated with the other related sub-plans.  There is some alignment and overlap, but also areas where the sub-plans are independent or have only a weak connection.  Potential for improved integration exists.
* **2 - Little Integration:** The current sub-plan has little integration with the other related sub-plans.  There is minimal overlap or synergy. The sub-plans primarily operate independently, and there may even be some conflicting goals or activities.
* **1 - Difficulty in Integration:** The current sub-plan is difficult to integrate with the other related sub-plans.  There are significant conflicts, redundancies, or a lack of alignment.  Integrating these sub-plans would require substantial revisions and coordination.

**Output Format:**

Provide your response in the following json format and make sure the json is valid:

```json
{{
    "Score": [Your Score (5, 4, 3, 2, or 1)],
    "Justification": [A concise explanation of your score, referencing specific elements from the Current Sub-Plan Objective, Current Sub-Plan Summary, and the objectives and summaries of the Other Related Sub-Plans.  Clearly describe the nature and extent of the integration.  Explain *why* you chose the score you did, providing specific examples and evidence for your assessment.  Mention which sub-plans integrate well, which integrate partially, and which show little or no integration.]
}}
```

**Example Input (Illustrative -  The actual input will be structured as described above):**

```
Current Sub-Plan Objective: To improve the digital literacy skills of senior citizens.
Current Sub-Plan Summary: This sub-plan will offer free computer classes to senior citizens, focusing on internet safety, email communication, and basic software applications.

Other Related Sub-Plans:
[
  {{
    "Related_Sub_Plan_Objective": "To provide access to affordable internet for low-income households.",
    "Related_Sub_Plan_Summary": "This sub-plan will subsidize internet service for eligible households and provide access to refurbished computers."
  }},
  {{
    "Related_Sub_Plan_Objective": "To develop online educational resources for all age groups.",
    "Related_Sub_Plan_Summary": "This sub-plan will create interactive online learning modules covering various subjects and skills."
  }}
]
```

**Example Output (Illustrative - The actual content would depend on the input):**

```json
{{
    "Score": "4",
    "Justification": "The current sub-plan (improving digital literacy for seniors) integrates well with the first related sub-plan (providing affordable internet). Access to internet is necessary for digital literacy, creating a strong synergy.  The current sub-plan also has some integration with the second related sub-plan (online educational resources), as these resources could be utilized by the seniors after developing their digital skills. However, the connection is less direct, as the online resources are for all age groups, not specifically designed for seniors. While there is strong alignment and synergy with one sub-plan and potential with the other, it's not a perfect integration as the connection to the second sub-plan is less focused.  Therefore, a score of 4 is appropriate."
}}
```

**Input Data**

Current Sub-Plan Objective: {objective}
Current Sub-Plan Summary: {summary}

Other Related Sub-Plans:
{other_objective_and_summary}

"""