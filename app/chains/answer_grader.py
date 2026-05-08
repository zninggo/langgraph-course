from typing import List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from app.graph.state import GraphState
from llm import llm


class AnswerGrader(BaseModel):
    binary_score: bool = Field(description="内容与回答相关为 yes 反之为 no")


def build_answer(state: GraphState) -> List[BaseMessage]:
    return [
        SystemMessage(content="""
            你是一名评分员，评估答案是否解决了某个问题 \n
            给出二进制分数“是”或“否”。“是”表示答案解决了问题。
        """),
        HumanMessage(content=f"""
            User question: \n\n {state.get('question')} \n\n LLM generation: {state.get('generation')}
        """),
    ]


answer_grader_chain = RunnableLambda(build_answer) | llm.with_structured_output(AnswerGrader, method="function_calling")
