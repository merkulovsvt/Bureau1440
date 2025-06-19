from datetime import datetime
from typing import Literal, List

from pydantic import BaseModel, Field, ConfigDict


class Question(BaseModel):
    id: int
    lesson: Literal['ai', 'math', 'python']
    question: str
    answer: str | None

    model_config = ConfigDict(extra='forbid')


class Answer(BaseModel):
    id: int
    q: str
    user_a: str
    real_a: str

    model_config = ConfigDict(extra='forbid')


class CriterionResult(BaseModel):
    mark: int = Field(ge=0, le=10)
    comment: str

    model_config = ConfigDict(extra='forbid')


class ModelResult(BaseModel):
    Completeness: CriterionResult
    Colorfulness: CriterionResult
    Structure: CriterionResult

    model_config = ConfigDict(extra='forbid')


class ExamResult(BaseModel):
    datetime: datetime
    form_data: List[Answer]
    ai_solution: List[ModelResult]

    model_config = ConfigDict(extra='forbid')
