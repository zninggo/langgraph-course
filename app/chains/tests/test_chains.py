import requests
from dotenv import load_dotenv

from app.chains.generation import generation_chain
from app.chains.hallucination_grader import hallucination_grader_chain, HallucinationGrader
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


def test_retrieval_generation_chain() -> None:
    question = "agent memory"
    docs = retriever.invoke(question)

    response = generation_chain.invoke({"question": question, "context": docs[0]})

    print(response)

def test_hallucination_grader_answer_no() -> None:
    """测试 hallucination_grader 是否正常格式化返回结果"""
    docs = retriever.invoke("agent memory")

    result: HallucinationGrader = hallucination_grader_chain.invoke(
        {"generation": 'In order to make pizza we need to first start with the dough', "documents": docs}
    )
    print(result)
    assert not result.binary_score