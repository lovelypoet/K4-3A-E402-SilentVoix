from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ai.quiz.schema import QuizDraft


class QuizProvider(ABC):
    provider_name = "unknown"

    @abstractmethod
    def generate_quiz_from_evidence(
        self, concept: dict[str, Any], evidence: list[dict[str, Any]], difficulty: str
    ) -> QuizDraft:
        raise NotImplementedError

