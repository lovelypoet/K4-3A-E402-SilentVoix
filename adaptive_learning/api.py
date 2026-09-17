from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, Any
from pydantic import BaseModel

from .models import RecommendationResponse
from .mastery import compute_mastery
from .graph import find_weak_prerequisite
from .mock_data import MOCK_CONCEPTS, MOCK_PREREQUISITES, MOCK_SOURCE_MAPPING, MOCK_STUDENT_ATTEMPTS

adaptive_router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])

def get_student_mastery_scores(student_id: str) -> Dict[str, Optional[float]]:
    """Helper to compute mastery for all concepts for a given student."""
    attempts = MOCK_STUDENT_ATTEMPTS.get(student_id, [])
    # Group attempts by concept
    concept_attempts = {}
    for a in attempts:
        cid = a["concept_id"]
        if cid not in concept_attempts:
            concept_attempts[cid] = []
        concept_attempts[cid].append(a)
        
    mastery_scores = {}
    for cid in MOCK_CONCEPTS.keys():
        if cid in concept_attempts:
            mastery_scores[cid] = compute_mastery(concept_attempts[cid])
        else:
            mastery_scores[cid] = None
    return mastery_scores

@adaptive_router.get("/recommendation/{student_id}", response_model=RecommendationResponse)
def get_recommendation(student_id: str, current_concept_id: str = "c6"):
    """
    Returns a recommendation based on the student's mastery and the current concept.
    """
    mastery_scores = get_student_mastery_scores(student_id)
    
    current_mastery = mastery_scores.get(current_concept_id)
    
    # If the student is already strong at the current concept, no need to recommend prereqs
    if current_mastery is not None and current_mastery >= 0.5:
        return RecommendationResponse(
            weak_concept="",
            recommended_concept="",
            reason="Student has mastered the current concept.",
            source={}
        )
        
    # Find weak prerequisite
    recommended_cid = find_weak_prerequisite(MOCK_PREREQUISITES, mastery_scores, current_concept_id)
    
    if recommended_cid == current_concept_id:
        reason = "No prerequisite — review this concept directly"
    else:
        reason = "Weak prerequisite"
        
    source = MOCK_SOURCE_MAPPING.get(recommended_cid, {})
    weak_concept_name = MOCK_CONCEPTS.get(current_concept_id, {}).get("name", "Unknown")
    recommended_concept_name = MOCK_CONCEPTS.get(recommended_cid, {}).get("name", "Unknown")
    
    return RecommendationResponse(
        weak_concept=weak_concept_name,
        recommended_concept=recommended_concept_name,
        reason=reason,
        source=source
    )
