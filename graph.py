import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import (JsonOutputParser,
                                           JsonOutputToolsParser,
                                           PydanticOutputParser,
                                           PydanticToolsParser)
from langchain_core.stores import InMemoryStore
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import Field

from chains import prompt
from schemas import AnswerQuestion

load_dotenv(override=True)

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
json_parser = JsonOutputToolsParser(return_id=True)
pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion])


class State(MessagesState):
    pass


graph = StateGraph(State)


def call_llm(state: State) -> State:

    chains = (
        llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
        | pydantic_parser
    )
    LLMMessage = chains.invoke(state.get('messages',[]))[-1]


    return State(messages=[AIMessage(content=LLMMessage.answer)])


graph.add_node("call_llm", call_llm)

graph.add_edge(START, "call_llm")
graph.add_edge("call_llm", END)

checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}

app = graph.compile(checkpointer=checkpointer)

# png = app.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png)

if __name__ == "__main__":
    print(f"hello reflexion agent")

    system_prompt = prompt.invoke({"messages": [HumanMessage("""
    撰写关于人工智能驱动的片上系统/自主片上系统问题领域的文章，
    列出从事该领域研究并已获得融资的初创公司。
    """)]})
    response = app.invoke(system_prompt, config)
    print(response)
# https://github.com/emarco177/langgraph-course/blob/project/reflexion-agent/chains.py
