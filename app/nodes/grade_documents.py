from typing import Dict

from app.chains.retrieval_grader import GradeDocuments, retrieval_grader
from app.graph.state import GraphState
from ingestion import retriever


def grade_documents(state: GraphState) -> Dict[str, any]:
    """检查检索的documents是否与问题有关系"""
    question = state["question"]

    documents = retriever.invoke(state["question"])
    filter_documents = []

    web_search = False

    for document in documents:
        result: GradeDocuments = retrieval_grader.invoke(
            {"question": question, "document": document}
        )

        grade = result.binary_score.lower()

        if grade == "yes":
            print("document 与内容相关...")
            filter_documents.append(document)
        else:
            print("document 与内容不相关...")
            web_search = True

    return {
        "documents": filter_documents,
        "web_search": web_search,
        "question": question,
    }
