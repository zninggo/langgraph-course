import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

load_dotenv(override=True)


@tool
def triple(number: float) -> float:
    """
    输入浮点数返回三倍的浮点数

    :param number: 一个浮点数
    :return: 三倍浮点数
    """
    return float(number) * 3


tools = [triple, TavilySearch(max_results=1)]

llm = ChatOpenAI(
    model='gpt-5.5',
    base_url=os.getenv('openai_base_url'),
    temperature=0.7
).bind_tools(tools)