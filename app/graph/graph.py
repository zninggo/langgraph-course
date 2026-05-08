from typing import Literal

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from app.chains.answer_grader import  answer_grader_chain
from app.chains.hallucination_grader import hallucination_grader_chain, HallucinationGrader
from app.graph.consts import (GENERATION_NODE, GRADE_DOCUMENTS_NODE,
                              RETRIEVE_NODES, SEARCH_NODE)
from app.graph.state import GraphState
from app.nodes import (generation_node, grade_documents, retrieve_nodes,
                       search_node)


def decide_to_generate(
    graph_state: GraphState,
) -> Literal[SEARCH_NODE, GENERATION_NODE]:
    if graph_state["web_search"] is True:
        return SEARCH_NODE
    else:
        return GENERATION_NODE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> Literal['useful', 'not useful', 'not supported']:
    print('----检查llm是否产生幻觉---')
    question = state["question"]
    generation = state["generation"]
    documents = state["documents"]

    score: HallucinationGrader = hallucination_grader_chain.invoke({
        "question": question,
        "generation": generation,
        "documents": documents,
    })
    print(f'hallucination_grader -> {score}')

    if hallucination_grader := score.binary_score:

        answer_score = answer_grader_chain.invoke({
            "question": question,
            "generation": generation,
        })

        print(f'answer_score -> {answer_score}')

        if answer_grader := answer_score.binary_score:


            print('--- llm 未产生幻觉 同时回答解决了问题 ---')
            return 'useful'

        else:
            print('--- 答案与问题无关 未解决问题 ---')
            return 'not useful'


    else:
        print('--- 内容与documents无关,重试---')
        return 'not supported'


graph = StateGraph(GraphState)

graph.add_node(SEARCH_NODE, search_node)
graph.add_node(GRADE_DOCUMENTS_NODE, grade_documents)
graph.add_node(RETRIEVE_NODES, retrieve_nodes)
graph.add_node(GENERATION_NODE, generation_node)


graph.add_edge(START, RETRIEVE_NODES)
graph.add_edge(RETRIEVE_NODES, GRADE_DOCUMENTS_NODE)
graph.add_edge(SEARCH_NODE, GENERATION_NODE)
# graph.add_edge(GENERATION_NODE, END)


graph.add_conditional_edges(GRADE_DOCUMENTS_NODE, decide_to_generate)

graph.add_conditional_edges(GENERATION_NODE, grade_generation_grounded_in_documents_and_question, {
    "useful": END,
    "not useful": SEARCH_NODE,
    "not supported": GENERATION_NODE,
})



app = graph.compile()

# png = app.get_graph().draw_mermaid_png()
#
# with open("./graph.png", "wb") as f:
#     f.write(png)

# print(app.get_graph().draw_mermaid())
# https://mermaid.live/

if __name__ == "__main__":
    result = app.invoke({"question": "什么是 agent memory? 请使用中文回答我"})
    print(result["generation"].split("<channel|>", 1)[-1])
    pass
