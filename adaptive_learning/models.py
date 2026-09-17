from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class Document(BaseModel):
    document_id: str
    title: str
    file_type: str  # "pdf", "pptx", "transcript"
    file_path: Optional[str] = None
    chunks_count: int = 0

class Chunk(BaseModel):
    chunk_id: str
    lesson_id: str
    text: str
    slide: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class ConceptNode(BaseModel):
    concept_id: str
    name: str
    description: Optional[str] = ""
    slide: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    mastery_state: Optional[str] = "not_learned"  # "current", "not_learned", "weak", "learning", "mastered"

class Relationship(BaseModel):
    source_concept_id: str
    target_concept_id: str
    relation_type: str = "prerequisite"

class SourceMapping(BaseModel):
    concept_id: str
    slide: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class Quiz(BaseModel):
    quiz_id: str
    concept_id: str
    question: str
    options: List[str]
    correct_option: int
    difficulty: float = 1.0

class StudentAnswer(BaseModel):
    quiz_id: str
    concept_id: str
    is_correct: bool
    difficulty: float = 1.0

class RecommendationResponse(BaseModel):
    weak_concept: str
    recommended_concept: str
    reason: str
    source: Dict[str, Any]  # e.g., {"slide": 17} or {"start_time": 581, "end_time": 600}

class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
