from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SourceReference:
    document_id: str
    chunk_id: Optional[str] = None
    slide: Optional[int] = None
    page: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    source_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "slide": self.slide,
            "page": self.page,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "source_type": self.source_type,
        }
        return {k: v for k, v in payload.items() if v is not None}


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    source: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Chunk":
        return cls(
            chunk_id=str(payload.get("chunk_id", "")),
            document_id=str(payload.get("document_id", "")),
            text=str(payload.get("text", "") or ""),
            source=dict(payload.get("source") or {}),
        )

    def to_source_reference(self) -> SourceReference:
        metadata = dict(self.source or {})
        return SourceReference(
            document_id=self.document_id,
            chunk_id=self.chunk_id,
            slide=metadata.get("slide"),
            page=metadata.get("page"),
            start_time=metadata.get("start_time"),
            end_time=metadata.get("end_time"),
            source_type=metadata.get("type"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "source": self.source,
        }


@dataclass
class Concept:
    id: str
    label: str
    description: str
    sources: list[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "sources": self.sources,
        }


@dataclass
class Relationship:
    source: str
    target: str
    relation: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "evidence": [{"chunk_id": e} for e in self.evidence],
        }


@dataclass
class KnowledgeGraph:
    lesson_id: str
    nodes: list[Concept] = field(default_factory=list)
    edges: list[Relationship] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


@dataclass
class Quiz:
    decision: str
    concept_id: str
    difficulty: str
    question: str = ""
    options: list[str] = field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    citations: list[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "concept_id": self.concept_id,
            "difficulty": self.difficulty,
            "question": self.question,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "citations": self.citations,
        }
