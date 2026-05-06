from typing import Dict

from app.graph.state import GraphState
from ingestion import retriever, vector_store


def retrieve_nodes(state: GraphState) -> Dict[str, any]:
    """检索节点 入口node"""

    print(f"检索节点已进入")
    question = state.get("question", "")
    documents = retriever.invoke(question)
    return {"question": question, "documents": documents}
