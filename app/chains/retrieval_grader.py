import re
from typing import List, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import (BaseOutputParser, JsonOutputParser,
                                           PydanticOutputParser)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from app.graph.state import GraphState
from llm import llm

# 基本不用 用下边的方法
# ChatPromptTemplate.from_messages()


class GradeDocuments(BaseModel):
    """检索内容的评分"""

    binary_score: str = Field(description="文档与问题是否相关 yes 或 no")

def build_messages(state) -> List[BaseMessage]:

    return [
        SystemMessage(content=f"""
        你是一个评分员，评估检索到的文档与用户问题的相关性。\n
        如果文档包含与问题相关的关键词或语义含义，则将其评为相关性。\n
        给出二进制分数“yes”或“no”，以表明该文件是否与问题相关。
        """),
        HumanMessage(
            content=f"检索文档：\n\n {state.get('document')} \n\n 用户问题：{state.get('question')}"
        ),
    ]

retrieval_grader = RunnableLambda(build_messages) | llm.with_structured_output(
    GradeDocuments
)
