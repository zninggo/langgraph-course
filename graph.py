import os
from typing import List, Literal, NotRequired

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers import (JsonOutputParser,
                                           JsonOutputToolsParser,
                                           PydanticOutputParser,
                                           PydanticToolsParser)
from langchain_core.stores import InMemoryStore
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import Field

from chains import call_llm_prompt, prompt, revise_prompt
from schemas import AnswerQuestion, ReviseAnswer
from tool_executor import tool_node

load_dotenv(override=True)

MAX_ITERATIONS = 2

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
json_parser = JsonOutputToolsParser(return_id=True)
pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion])


class State(MessagesState):
    search_queries: NotRequired[List[str]]
    pass


graph = StateGraph(MessagesState)


def draft_node(state: MessagesState) -> MessagesState:
    """llm生成草稿内容"""
    print('大脑正在思考...')
    chains = llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
    response = chains.invoke(state.get("messages", []))
    return State(messages=[response])

def revise_node(state: MessagesState) -> MessagesState:
    """修订文章内容"""
    print('大脑正在思考...')

    revise_llm = revise_prompt | llm.bind_tools(tools=[ReviseAnswer],tool_choice="ReviseAnswer")
    response = revise_llm.invoke(state.get("messages", []))
    return State(messages=[response])



def event_loop(state: MessagesState) -> Literal["executor_tools", END]:
    """迭代处理文章内容 处理路由"""

    iterations = sum(isinstance(message,ToolMessage) for message in state.get("messages", []))
    if iterations > MAX_ITERATIONS:
        return END

    return 'executor_tools'


graph.add_node("draft_node", draft_node)
graph.add_node("executor_tools", tool_node)
graph.add_node("revise_node", revise_node)

graph.add_edge(START, "draft_node")
graph.add_edge("draft_node", "executor_tools")
graph.add_edge("executor_tools", "revise_node")

graph.add_conditional_edges("revise_node", event_loop)
# graph.add_edge("draft_node", END)

checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}

app = graph.compile(checkpointer=checkpointer)

print(app.get_graph().draw_mermaid())
# png = app.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png)

if __name__ == "__main__":
    print(f"hello reflexion agent")

    system_prompt = call_llm_prompt.invoke({"messages": [HumanMessage("""
    撰写关于人工智能驱动的片上系统/自主片上系统问题领域的文章，
    列出从事该领域研究并已获得融资的初创公司。
    """)]})
    response = app.invoke(system_prompt, config)
    print(response)

    message = response["messages"][-1]
    if isinstance(message, AIMessage) and message.tool_calls is not None:
        print(message.tool_calls[0].get('args', {}).get('answer', {}))
    else:
        print(message)
# https://github.com/emarco177/langgraph-course/blob/project/reflexion-agent/chains.py
