from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

load_dotenv(override=True)
tool_node = ToolNode(
    [
        TavilySearch(
            max_results=5,
            topic="general",
        )
    ]
)
