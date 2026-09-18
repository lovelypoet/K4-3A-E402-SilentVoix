from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

class Document(BaseModel):
    document_id: str
    title: str
    file_type: str  # "pdf", "pptx", "video", "docx", "text"
    file_path: Optional[str] = None
    video_url: Optional[str] = None
    slide_url: Optional[str] = None
    lesson_id: Optional[str] = None
    chunks_count: int = 0
    source_key: Optional[str] = None
    source_group: Optional[str] = None
    status: Optional[str] = "READY"
    error_code: Optional[str] = None

class Lesson(BaseModel):
    lesson_id: str
    title: str
    video_url: Optional[str] = None
    slide_url: Optional[str] = None
    file_path: Optional[str] = None
    total_slides: Optional[int] = 0
    duration_seconds: Optional[float] = 0
    source_type: Optional[str] = None  # "video" | "slide" | "document"
    source_key: Optional[str] = None
    source_group: Optional[str] = None
    status: Optional[str] = "READY"
    error_code: Optional[str] = None


class VideoLinkRequest(BaseModel):
    """Chỉ dán link VIDEO (YouTube)."""
    video_url: str = Field(..., description="Link YouTube (bắt buộc)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        }
    }


class SlideLinkRequest(BaseModel):
    """Link Google Docs / Slides / Drive / file .pdf/.pptx/.docx."""
    slide_url: str = Field(..., description="Link docs.google / drive / PDF / PPTX / DOCX")

    model_config = {
        "json_schema_extra": {
            "example": {
                "slide_url": "https://docs.google.com/document/d/FILE_ID/edit"
            }
        }
    }


class Chunk(BaseModel):
    chunk_id: str
    lesson_id: str
    document_id: Optional[str] = None
    text: str
    slide: Optional[int] = None
    page: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    source_key: Optional[str] = None
    source_group: Optional[str] = None
    source_type: Optional[str] = None

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
    quiz_id: Optional[str] = None  # Để trống thì tự động sinh (e.g. quiz_01, quiz_02,...)
    concept_id: str = "c6"
    is_correct: bool = True
    difficulty: float = 1.0

class RecommendationResponse(BaseModel):
    weak_concept: str
    recommended_concept: str
    reason: str
    source: Dict[str, Any]  # e.g., {"slide": 17} or {"start_time": 581, "end_time": 600}

class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
