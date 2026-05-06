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


# 返回json -> dict 格式
# parser = JsonOutputParser(pydantic_object=GradeDocuments)
# 返回json -> pydantic 格式
parser = PydanticOutputParser(pydantic_object=GradeDocuments)

"""
● ┌──────────┬──────────────────┬─────────────────────────────────────┐
  │          │ JsonOutputParser │        PydanticOutputParser         │
  ├──────────┼──────────────────┼─────────────────────────────────────┤
  │ 返回类型 │ dict             │ Pydantic 模型实例                   │
  ├──────────┼──────────────────┼─────────────────────────────────────┤
  │ 访问方式 │ result["key"]    │ result.key                          │
  ├──────────┼──────────────────┼─────────────────────────────────────┤
  │ 格式指令 │ 注入 JSON schema │ 注入 JSON schema + 要求严格匹配模型 │
  ├──────────┼──────────────────┼─────────────────────────────────────┤
  │ 类型验证 │ 无               │ 自动验证并转换类型                  │
  └──────────┴──────────────────┴─────────────────────────────────────┘

  简单说：PydanticOutputParser = JsonOutputParser + 自动转 Pydantic 对象。

  你的场景用 PydanticOutputParser 更合适，result.binary_score 就能直接访问了。
"""


def build_messages(state) -> List[BaseMessage]:

    return [
        SystemMessage(content=f"""
        你是一个评分员，评估检索到的文档与用户问题的相关性。\n
        如果文档包含与问题相关的关键词或语义含义，则将其评为相关性。\n
        给出二进制分数“yes”或“no”，以表明该文件是否与问题相关。
        
        {parser.get_format_instructions()}
        """),
        HumanMessage(
            content=f"检索文档：\n\n {state.get('document')} \n\n 用户问题：{state.get('question')}"
        ),
    ]


"""
  你用的 LLM 类不支持 with_structured_output。常见原因：
  1. 本地模型（LM Studio/Ollama） — 模型本身不支持 function calling
  2. 用了 ChatOllama 以外的封装类
  解决方案：用输出解析器替代
"""
# 报错 llm.with_structured_output(GradeDocuments)
# retrieval_grader = RunnableLambda(build_messages) | llm.with_structured_output(GradeDocuments)

retrieval_grader = RunnableLambda(build_messages) | llm | parser
