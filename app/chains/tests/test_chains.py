import requests
from dotenv import load_dotenv

from app.chains.retrieval_grader import GradeDocuments, retrieval_grader
from ingestion import retriever

load_dotenv(override=True)


def test_retrieval_grader_answer_no() -> None:
    """测试retrieval是否正常格式化返回结果"""
    question = "agent memory"
    docs = retriever.invoke(question)
    result: GradeDocuments = retrieval_grader.invoke(
        {"question": question, "document": docs[0]}
    )
    print(result)
    assert result.binary_score == "yes"
