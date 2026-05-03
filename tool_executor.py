from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode
from typing import List, Literal, NotRequired

from schemas import AnswerQuestion,ReviseAnswer

load_dotenv(override=True)


tavily_tool = TavilySearch(
    max_results=5,
)

def search_query(queries: List[str], **kwargs):
    """网络查询关键字内容"""
    return tavily_tool.batch(inputs=[{'query':query} for query in queries])

tool_node = ToolNode(
    [
        StructuredTool.from_function(search_query,name=AnswerQuestion.__name__),
        StructuredTool.from_function(search_query,name=ReviseAnswer.__name__),
     ]
)