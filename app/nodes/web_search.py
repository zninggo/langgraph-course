from typing import Dict

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_tavily import TavilySearch

from app.graph.state import GraphState

load_dotenv(override=True)

search_tool = TavilySearch(max_results=3)


def search_node(state: GraphState) -> Dict[str, any]:
    """需要网络搜索的节点"""
    print('开始网络搜索了...')
    question = state["question"]
    documents = state["documents"]

    response = search_tool.invoke({"query": question})

    web_search_results = "\n".join(
        [result["content"] for result in response["results"]]
    )

    print(web_search_results)

    if documents is not None:
        documents.append(Document(page_content=web_search_results))
    else:
        documents = [Document(page_content=web_search_results)]

    return {"question": question, "documents": documents, "web_search": False}


if __name__ == "__main__":
    search_node({"question": "langchain 是什么", "documents": None})
