from typing import List

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from app.graph.state import GraphState
from llm import llm

# https://github.com/emarco177/langgraph-course/commit/5400fb70faa11817c1ef807d3bbe4efd76c55ae7#diff-9c9f2d2d3694b46edcdfcd309f8b28a1b7048bd320b58c2a51a5be193c7cfb7a


class HallucinationGrader(BaseModel):
    """评估llm的答案是否有数据支持"""
    binary_score: bool = Field(description='yes 表示答案有事实依据，no 表示答案是幻觉/无事实支持')


def build_messages(state: GraphState) -> List[BaseMessage]:
    return [
        SystemMessage(content=f"""
            你是评分员，评估LLM生成的答案是否由提供的事实集合直接支持。

            判断标准：
            - "yes"：答案中的核心信息可以从事实集合中找到依据
            - "no"：答案包含事实集合中没有的信息，或与事实无关
            """),
        HumanMessage(content=f"""
            事实集合：\n\n {state.get('documents')} \n\n LLM 答案：{state.get('generation')}
        """)
    ]


hallucination_grader_chain = RunnableLambda(build_messages) | llm.with_structured_output(HallucinationGrader, method="function_calling")
"""
  method="function_calling" 根本原因：

  - json_schema 方法（pydantic v2 默认）：要求 content 是纯 JSON
  - function_calling 方法：从 tool_calls 取值，忽略 content

  你的 thinking 模型 content 带 {thinking}...，用 json_schema 就炸了，用 function_calling 就正常。
"""