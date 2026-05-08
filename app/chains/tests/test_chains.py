import requests
from dotenv import load_dotenv

from app.chains.generation import generation_chain
from app.chains.hallucination_grader import (HallucinationGrader,
                                             hallucination_grader_chain)
from app.chains.retrieval_grader import GradeDocuments, retrieval_grader
from app.chains.router import router_query_chain, RouterQuery
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
        {
            "generation": "In order to make pizza we need to first start with the dough",
            "documents": docs,
        }
    )
    print(result)
    assert not result.binary_score


def test_router_query_to_vectorstore() -> None:
    """测试router是否能路由到向量数据库"""
    result:RouterQuery = router_query_chain.invoke({"question": "agent memory"})
    print(result)
    assert result.datasource == 'vectorstore'

def test_router_query_to_websearch() -> None:
    """测试router是否能路由到网络搜索"""
    result:RouterQuery = router_query_chain.invoke({"question": "披萨好吃吗"})
    print(result)
    assert result.datasource == 'websearch'