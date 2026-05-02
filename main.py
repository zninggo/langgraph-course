from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph

from nodes import run_agent_reasoning, tool_node

load_dotenv(override=True)

AGENT_REASON = "agent_reason"
ACT = "act"
LAST = -1


def should_continue(state: MessagesState) -> str:
    if not state["messages"][LAST].tool_calls:
        return END
    return ACT


flow = StateGraph(MessagesState)

flow.add_node(AGENT_REASON, run_agent_reasoning)
flow.add_node(ACT, tool_node)

# flow.set_entry_point(AGENT_REASON)

flow.add_edge(START, AGENT_REASON)
flow.add_edge(ACT, AGENT_REASON)

flow.add_conditional_edges(
    AGENT_REASON,
    should_continue,
    {
        END: END,
        ACT: ACT,
    },
)

app = flow.compile()
png = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png)


def main():
    print("Hello from langgraph-course!")

    response = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="东京的天气怎么样? 列出温度清单然后通过triple 翻三倍"
                )
            ]
        }
    )
    print(response.get("messages")[LAST].content)


if __name__ == "__main__":
    main()
