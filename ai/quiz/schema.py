from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


QuizDecision = Literal[
    "GENERATE_QUIZ",
    "DISAMBIGUATE",
    "REFUSE_UNGROUNDED",
    "VALIDATION_FAILED",
    "GENERATION_FAILED",
]


class QuizOption(BaseModel):
    id: str
    text: str


class QuizCitation(BaseModel):
    document_id: str | None = None
    chunk_id: str
    page: int | None = None
    slide: int | None = None
    start_time: float | None = None
    end_time: float | None = None


class QuizValidation(BaseModel):
    passed: bool
    reason: str | None = None


class Quiz(BaseModel):
    quiz_id: str
    lesson_id: str
    concept_id: str
    concept_label: str
    difficulty: Literal["easy", "medium", "hard"]
    question: str = ""
    options: list[QuizOption] = Field(default_factory=list)
    correct_option: str = ""
    explanation: str = ""
    citations: list[QuizCitation] = Field(default_factory=list)
    decision: QuizDecision
    validation: QuizValidation
    generator_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QuizDraft(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str
    used_evidence_ids: list[str] = Field(default_factory=list)
