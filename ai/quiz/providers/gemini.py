from __future__ import annotations

import json
import logging
import random
import time
from typing import Any

import httpx

from ai.config import get_config
from ai.quiz.health import record
from ai.quiz.schema import QuizDraft
from .base import QuizProvider

logger = logging.getLogger(__name__)


class ProviderOutputError(ValueError):
    """The provider responded, but its structured quiz draft was not valid."""


class ProviderRateLimitError(RuntimeError):
    """Gemini returned a rate/quota response after bounded handling."""


GROUNDED_QUIZ_PROMPT = """You generate educational multiple-choice questions.

STRICT RULES:
1. Use ONLY the supplied source evidence.
2. Do not rely on outside knowledge.
3. Generate exactly four answer options.
4. Exactly one option must be correct.
5. Distractors must be plausible but incorrect according to the evidence.
6. The explanation must be fully supported by the evidence.
7. Do not mention information not contained in the evidence.
8. Respect the requested difficulty.
9. Return JSON only with the requested fields.
10. The question must be at most 25 words.
11. Every option must be at most 12 words.
12. The explanation must be at most 40 words.
Count words before returning JSON. Prefer concise wording over extra detail.

Difficulty guidance:
- easy: direct recall/basic understanding.
- medium: application or combination of supported facts.
- hard: multi-step reasoning/comparison/synthesis fully supported by evidence.

Creativity guidance:
- Vary the question style when the evidence permits: use a short realistic scenario,
  compare two supported ideas, ask about a consequence, or target a likely misconception.
- Avoid repetitive wording and generic distractors.
- Never add a scenario detail, fact, or distractor that is not supported by the evidence.

If the evidence cannot support a question, return an empty question, empty options,
correct_index -1, an explanation stating that evidence is insufficient, and an empty
used_evidence_ids list.

CONCEPT:
{concept_label}

REQUESTED DIFFICULTY:
{difficulty}

SOURCE EVIDENCE:
{evidence}

Return exactly this JSON shape:
{{"question":"...","options":["...","...","...","..."],"correct_index":0,"explanation":"...","used_evidence_ids":["E1"]}}
"""


class GeminiProvider(QuizProvider):
    provider_name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float | None = None, max_retries: int = 3, sleep_fn=None, random_fn=None, http_post=None):
        self.api_key = api_key or get_config("GEMINI_API_KEY")
        self.model = model or get_config("QUIZ_MODEL", "gemini-3.6-flash")
        try:
            configured_timeout = float(get_config("QUIZ_LLM_TIMEOUT_SECONDS", "30") or 30)
        except ValueError:
            configured_timeout = 30.0
        self.timeout = timeout if timeout is not None else configured_timeout
        self.max_retries = max(1, min(3, max_retries))
        self.sleep_fn = sleep_fn or time.sleep
        self.random_fn = random_fn or random.uniform
        self.http_post = http_post or httpx.post
        self.last_request_metrics: dict[str, Any] = {}

    def build_prompt(self, concept: dict[str, Any], evidence: list[dict[str, Any]], difficulty: str) -> str:
        evidence_text = []
        for item in evidence:
            evidence_text.append(f"{item.get('_evidence_id')} : {item.get('text', '')}")
        return GROUNDED_QUIZ_PROMPT.format(
            concept_label=str(concept.get("label") or concept.get("id") or ""),
            difficulty=difficulty,
            evidence="\n\n".join(evidence_text),
        )

    def generate_quiz_from_evidence(self, concept: dict[str, Any], evidence: list[dict[str, Any]], difficulty: str) -> QuizDraft:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        prompt = self.build_prompt(concept, evidence, difficulty)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.7,
                "topP": 0.9,
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "question": {"type": "STRING"},
                        "options": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "correct_index": {"type": "INTEGER"},
                        "explanation": {"type": "STRING"},
                        "used_evidence_ids": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["question", "options", "correct_index", "explanation", "used_evidence_ids"],
                },
            },
        }
        started = time.perf_counter()
        attempts = 0
        status_code = None
        response = None
        try:
            for attempt in range(1, self.max_retries + 1):
                attempts = attempt
                response = self.http_post(
                    url,
                    headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
                    json=payload,
                    timeout=self.timeout,
                )
                status_code = response.status_code
                if status_code != 503:
                    if status_code == 429:
                        record("429_count")
                        body = response.text.lower()
                        if "insufficient_quota" in body or "credit_balance_exhausted" in body:
                            raise ProviderRateLimitError("PROVIDER_RATE_LIMIT")
                        if attempt >= min(self.max_retries, 2):
                            raise ProviderRateLimitError("PROVIDER_RATE_LIMIT")
                        retry_after = response.headers.get("retry-after")
                        try:
                            delay = min(5.0, max(0.0, float(retry_after))) if retry_after else 1.0
                        except ValueError:
                            delay = 1.0
                        self.sleep_fn(delay + self.random_fn(0, 0.25))
                        continue
                    response.raise_for_status()
                    break
                record("503_count")
                if attempt < self.max_retries:
                    self.sleep_fn((2 ** (attempt - 1)) + self.random_fn(0, 0.25))
            else:
                response.raise_for_status()
        finally:
            self.last_request_metrics = {
                "provider": self.provider_name,
                "model": self.model,
                "attempt_count": attempts,
                "http_status": status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        data = response.json()
        try:
            raw = data["candidates"][0]["content"]["parts"][0]["text"]
            return QuizDraft.model_validate(json.loads(raw))
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ProviderOutputError(f"Malformed Gemini quiz JSON: {exc}") from exc
