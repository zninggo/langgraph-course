from pydantic import BaseModel, Field


class Reflexion(BaseModel):
    missing: str = Field(description="缺失内容的评价")
    superfluous: str = Field(description="多余内容的评价")


class AnswerQuestion(BaseModel):
    answer: str = Field(description="详细回答")
    reflexion: Reflexion = Field(description="你对初始答案的反思")
