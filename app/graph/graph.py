from typing import Literal

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.graph.consts import SEARCH_NODE, GRADE_DOCUMENTS_NODE, RETRIEVE_NODES, GENERATION_NODE
from app.graph.state import GraphState
from app.nodes import search_node, grade_documents, retrieve_nodes, generation_node


def decide_to_generate(graph_state: GraphState) -> Literal[SEARCH_NODE,GENERATION_NODE]:
    if graph_state['web_search'] is True:
        return SEARCH_NODE
    else:
        return GENERATION_NODE

graph = StateGraph(GraphState)

graph.add_node(SEARCH_NODE,search_node)
graph.add_node(GRADE_DOCUMENTS_NODE,grade_documents)
graph.add_node(RETRIEVE_NODES,retrieve_nodes)
graph.add_node(GENERATION_NODE,generation_node)


graph.add_edge(START, RETRIEVE_NODES)
graph.add_edge(RETRIEVE_NODES, GRADE_DOCUMENTS_NODE)
graph.add_edge(SEARCH_NODE, GENERATION_NODE)
graph.add_edge( GENERATION_NODE,END)


graph.add_conditional_edges(GRADE_DOCUMENTS_NODE, decide_to_generate)

app = graph.compile()

png = app.get_graph().draw_mermaid_png()

with open('./graph.png','wb') as f:
    f.write(png)

if __name__ == '__main__':
    result = app.invoke({'question': '什么是 agent memory? 请使用中文回答我'})
    print(result['generation'].split('<channel|>',1)[-1])
    pass

