import os

from dotenv import load_dotenv
from langchain_core.output_parsers import (JsonOutputParser,
                                           JsonOutputToolsParser,
                                           PydanticOutputParser,
                                           PydanticToolsParser)
from langchain_core.stores import InMemoryStore
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState, StateGraph
from pydantic import Field

from schemas import AnswerQuestion

load_dotenv(override=True)


class State(MessagesState):
    system_prompt: str


graph = StateGraph(State)

checkpointer = InMemorySaver()

config = {"configurable": {"thread_id": "1"}}

app = graph.compile(checkpointer=checkpointer)

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
json_parser = JsonOutputToolsParser(return_id=True)
pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion])
