from datetime import datetime
from pydantic import BaseModel
from typing import Literal, List


class Question(BaseModel):
    id: int
    lesson: Literal['ai', 'math', 'python']
    question: str
    answer: str


class Answer(BaseModel):
    id: int
    q: str
    user_a: str
    real_a: str


class CriterionResult(BaseModel):
    mark: int
    comment: str


class ModelResult(BaseModel):
    Completeness: CriterionResult
    Colorfulness: CriterionResult
    Structure: CriterionResult


class ExamResult(BaseModel):
    datetime: datetime
    form_data: List[Answer]
    ai_solution: List[ModelResult]
