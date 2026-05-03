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

prompt = prompt_messages.partial(time=lambda: datetime.datetime.now().isoformat())

call_llm_prompt = prompt.partial(first="提供一个详细的答案")

revise_instructions = """用新信息修改你之前的答案.
    - 你应该利用之前的批评为你的答案添加重要信息。
        - 您必须在修订后的答案中包含数字引用，以确保可验证。
        - 在答案底部添加“参考文献”部分（不计入字数限制）。形式为:
            - [1] https://example.com
            - [2] https://example.com
    - 你应该用之前的点评来剔除多余的信息，并确保答案不超过250字.
"""

revise_prompt = prompt.partial(first=revise_instructions)


if __name__ == "__main__":
    print(revise_prompt)

