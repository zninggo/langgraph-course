import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
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
    model=os.getenv("OPENAI_MODEL"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
).bind_tools(tools)


if __name__ == "__main__":
    r = llm.invoke(
        [
            SystemMessage(
                content="你是一个非常乐于助人好帮手，可以使用tools来回答问题"
            ),
            HumanMessage(content="今天天气怎么样"),
        ]
    )

    print(r)
