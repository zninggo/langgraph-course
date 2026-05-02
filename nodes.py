from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from react import llm, tools

load_dotenv(override=True)

SYSTEM_MESSAGE = """
你是一个非常乐于助人好帮手，可以使用tools来回答问题
"""


def run_agent_reasoning(state: MessagesState) -> MessagesState:


    response = llm.invoke(
        [SystemMessage(content=SYSTEM_MESSAGE), *state.get("messages")],
    )
    print(response)

    return MessagesState(messages=[response])


tool_node = ToolNode(tools=tools)
