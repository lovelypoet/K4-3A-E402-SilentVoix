from pydantic import BaseModel
from typing import Optional, Dict, Any

class StudentAnswer(BaseModel):
    quiz_id: str
    concept_id: str
    is_correct: bool
    difficulty: float

class ConceptNode(BaseModel):
    concept_id: str
    name: str
    mastery_state: str  # "current", "not_learned", "weak", "learning", "mastered"
    # additional metadata can go here if needed

class RecommendationResponse(BaseModel):
    weak_concept: str
    recommended_concept: str
    reason: str
    source: Dict[str, Any]  # e.g., {"slide": 17} or {"start_time": 581, "end_time": 600}
