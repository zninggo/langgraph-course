from typing import List

from pydantic import BaseModel, Field


class Reflexion(BaseModel):
    """你对问题的反思"""

    missing: str = Field(description="缺失内容的评价")
    superfluous: str = Field(description="多余内容的评价")


class AnswerQuestion(BaseModel):
    """你对问题的回答和反思"""

    answer: str = Field(description="详细回答")
    reflexion: Reflexion = Field(description="你对初始答案的反思")
    search_queries: List[str] = Field(description="1到3个搜索查询以研究改进方案")


class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question."""

    references: List[str] = Field(
        description="Citations motivating your updated answer."
    )