import operator
from typing import TypedDict

from langgraph.graph import StateGraph, START,END


class State(TypedDict):
    nlist: str

def node_a (state:State) -> State:
    print(f'node a 接收了参数: {state}')

    node = 'hello world node a'

    return State(nlist=node)


graph = StateGraph(State)

graph.add_node('a',node_a)
graph.add_edge(START,'a')
graph.add_edge('a',END)


app = graph.compile()

# print(app.get_graph().draw_png('draw.png'))
if __name__ == "__main__":
    print("hello langgraph")

    print(app.invoke(State(nlist='hello world')))
