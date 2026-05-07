from typing import List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

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


"""
 因为 with_structured_output 走的是 tool_calls 通道，不是 content。

  模型返回的数据结构大概长这样：

  {
    "content": "<|channel>thought\n思考过程...\n<channel|>",
    "tool_calls": [{"function": {"name": "GradeDocuments", "arguments": "{\"binary_score\": \"yes\"}"}}]
  }

  - content — 思考过程（被忽略）
  - tool_calls — 结构化数据（with_structured_output 读这个）

  LangChain 的 with_structured_output 直接从 tool_calls 里提取 Pydantic 对象，根本不看 content，所以思考内容自然被过滤了。

  这就是为什么 with_structured_output 比 PydanticOutputParser 更好——不依赖模型的文本输出格式，不怕思考内容、不怕格式错误。
"""
retrieval_grader = RunnableLambda(build_messages) | llm.with_structured_output(
    GradeDocuments, method="function_calling"
)
