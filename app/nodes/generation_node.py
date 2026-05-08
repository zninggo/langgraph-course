from typing import Dict

from app.chains.generation import generation_chain
from app.graph.state import GraphState


def generation_node(state: GraphState) -> Dict[str, any]:

    question = state["question"]
    documents = state["documents"]
    context = "\n".join([doc.page_content for doc in documents])

    generation = generation_chain.invoke({"question": question, "context": context})

    print("----------结果已出----------")

    return {
        "question": question,
        "documents": documents,
        "generation": generation,
    }
