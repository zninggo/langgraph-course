from typing import Literal, List

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from app.graph.state import GraphState
from llm import llm


class RouterQuery (BaseModel):
    """决定数据源是向量数据库还是网络搜索"""
    datasource: Literal['vectorstore', 'websearch'] = Field(..., description="""遇到问题时判断是使用向量数据库还是进行网络搜索""")



def build_messages(state: GraphState) -> List[BaseMessage]:

    return [
        SystemMessage(content="""
            你擅长将用户问题引导到矢量商店或网页搜索。
            The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.
            在这些主题上可以使用矢量商店提问。其他情况则使用网页搜索
        """),
        HumanMessage(content=f"""
            question: {state.get('question')}
        """)
    ]


router_query_chain = RunnableLambda(build_messages) | llm.with_structured_output(RouterQuery, method="function_calling")