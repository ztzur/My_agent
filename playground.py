import pandas as pd
import configs.general.config as c


# programs = pd.read_csv(c.programs_path)
# sub = pd.read_csv(c.subjects_path)
#
# diff = set(sub.Name) - set(programs['תת סל'])
#
# sub.Name = sub.Name.replace('קידום שלומות [well-being] של צוותי חינוך', 'קידום שלומות (well being) של צוותי חינוך')
# programs['תת סל'] = programs['תת סל'].replace('מנהיגות ומוערבות בלמידה', 'מנהיגות ומעורבות בלמידה')
#
# programs.to_csv(c.programs_path, index=False, encoding='utf-8-sig')
# sub.to_csv(c.subjects_path, index=False, encoding='utf-8-sig')
import multiprocessing as mp
import utils


llm = utils.connect_to_llm(endpoint='azure')

def test(x):
    ans = llm.invoke(f'add each number in this list by 2: {x}')

    return ans


def main():
    test_list = [
        [1, 4, 6],
        [7, 8, 9],
        [10, 11, 12],
    ]

    # Initialize pool
    with mp.Pool(processes=3) as pool:
        all_results = []
        # Loop through the test_list
        for l in test_list:
            # Use pool.starmap to process the list
            # Note: pool.map is preferred here since args are single values, not tuples
            res = pool.map(test, l)
            all_results.append(res)

        # Flatten the results if needed, e.g., for a single list
        flattened_results = [item for sublist in all_results for item in sublist]
        print(flattened_results)

        # If you need the results as lists of results e.g., per sublist in test_list
        print(all_results)


if __name__ == "__main__":
    main()
