from dotenv import load_dotenv
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from react import llm,tools

load_dotenv(override=True)

SYSTEM_MESSAGE = """
你是一个非常乐于助人好帮手，可以使用tools来回答问题
"""


def run_agent_reasoning(state: MessagesState) -> MessagesState:


    print(state.get("messages"))

    response = llm.invoke([{"role": "system", "content": SYSTEM_MESSAGE}, *state.get("messages")])

    return MessagesState(messages=[response])


tool_node = ToolNode(tools=tools)