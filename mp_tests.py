import multiprocessing as mp
from utils import connect_to_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


llm = connect_to_llm(endpoint='azure')


def func(x, prompt):
    content_prompt = PromptTemplate.from_template(template=prompt)
    content_chain = content_prompt | llm | StrOutputParser()

    return content_chain.invoke(x)


if __name__ == '__main__':
    prompt_1 = """Tell me a joke about: {sub}"""
    prompt_2 = """Calculate {sub} by the power of two"""
    prompt_3 = """What band plays this song: {sub}"""

    func_list = [
        {'x': 'dogs', 'prompt': prompt_1},
        {'x': 7, 'prompt': prompt_2},
        {'x': 'come out and play', 'prompt': prompt_3},
    ]
    with mp.Manager() as manager:
        d_1 = manager.dict()
        d_1['sub'] = 'dogs'
        d_2 = manager.dict()
        d_2['sub'] = 7
        d_3 = manager.dict()
        d_3['sub'] = 'come out and play'

        test = [
            (d_1, prompt_1),
            (d_2, prompt_2),
            (d_3, prompt_3),
        ]
        with manager.Pool(processes=3) as p:
            res = p.starmap(func, test)

    for i in res:
        print(i)
