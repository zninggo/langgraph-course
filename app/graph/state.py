from typing import List, Literal, TypedDict

from langchain_core.documents import Document


class GraphState(TypedDict):
    """
    langgraph 中的 全局状态

    属性:
        question: 问题
        generation: 答案
        web_search: 是否需要网络搜索
        documents: 文档列表
    """

    question: str
    generation: str
    web_search: bool
    documents: List[Document]
