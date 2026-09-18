from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from adaptive_learning.storage import db_storage
from ai.extraction.normalizer import canonical_concept_id
from ai.pipeline import build_graph
from ai.quiz.grounded import generate_grounded_quiz
from ai.quiz.health import summary as quiz_health_summary
from ai.quiz.providers.gemini import GeminiProvider


router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


class QuizGenerateRequest(BaseModel):
    lesson_id: str
    concept_id: str
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    allow_deterministic_fallback: bool = False


def _lesson_graph(lesson_id: str, requested_concept_id: str) -> dict:
    raw_chunks = db_storage.get_chunks_by_lesson(lesson_id)
    if not raw_chunks:
        raise HTTPException(status_code=400, detail="Lesson has no ingested evidence chunks")
    ai_chunks = [
        {
            "chunk_id": chunk.get("chunk_id"),
            "document_id": chunk.get("document_id") or lesson_id,
            "text": chunk.get("text"),
            "source": {
                "document_id": chunk.get("document_id") or lesson_id,
                "chunk_id": chunk.get("chunk_id"),
                "page": chunk.get("page"),
                "slide": chunk.get("slide"),
                "start_time": chunk.get("start_time"),
                "end_time": chunk.get("end_time"),
                "text": chunk.get("text"),
            },
        }
        for chunk in raw_chunks
    ]
    graph = build_graph(ai_chunks, lesson_id=lesson_id)
    concept_info = next((item for item in db_storage.get_concepts_by_lesson(lesson_id) if item.get("concept_id") == requested_concept_id), None)
    wanted_canonical = canonical_concept_id((concept_info or {}).get("name", requested_concept_id))
    target = next((node for node in graph.get("nodes", []) if node.get("id") == wanted_canonical), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Concept is not supported by the ingested lesson evidence")
    if requested_concept_id != wanted_canonical:
        target["id"] = requested_concept_id
        for edge in graph.get("edges", []):
            if edge.get("source") == wanted_canonical: edge["source"] = requested_concept_id
            if edge.get("target") == wanted_canonical: edge["target"] = requested_concept_id
    return graph


@router.post("/generate")
def generate_quiz(request: QuizGenerateRequest):
    if not db_storage.get_lesson(request.lesson_id):
        raise HTTPException(status_code=404, detail=f"Lesson not found: {request.lesson_id}")
    graph = _lesson_graph(request.lesson_id, request.concept_id)
    result = generate_grounded_quiz(
        graph=graph, lesson_id=request.lesson_id, concept_id=request.concept_id,
        difficulty=request.difficulty, provider=GeminiProvider(),
        allow_deterministic_fallback=request.allow_deterministic_fallback,
    )
    return result.model_dump()


@router.get("/health")
def quiz_provider_health():
    return quiz_health_summary()
