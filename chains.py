import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_messages = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    你是一位研究专家。
    当前时间：
        {time}
    
    1. {first}
    2. 反思并批判你的答案。要严格要求，以最大限度地改进。
    3. 推荐搜索查询以查找信息并改进你的答案。
    """,
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "请使用规定的格式回答上述用户的问题。"),
    ]
)

prompt = prompt_messages.partial(
    time=lambda: datetime.datetime.now().isoformat(), first="提供一个详细的答案"
)

if __name__ == "__main__":
    print(prompt)
