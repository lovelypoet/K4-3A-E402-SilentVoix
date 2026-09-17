from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from .models import (
    RecommendationResponse, 
    StudentAnswer, 
    Document, 
    Chunk, 
    GraphResponse,
    ConceptNode
)
from .mastery import compute_mastery, compute_mastery_state
from .graph import find_weak_prerequisite
from .mock_data import MOCK_CONCEPTS, MOCK_PREREQUISITES, MOCK_SOURCE_MAPPING, MOCK_STUDENT_ATTEMPTS
from .source_mapper import SourceMapper
from .ingestion import DocumentIngestor

adaptive_router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])
source_mapper = SourceMapper()

# In-memory database of attempts for demonstration
STUDENT_ATTEMPTS_DB = dict(MOCK_STUDENT_ATTEMPTS)

def get_student_mastery_scores(student_id: str) -> Dict[str, Optional[float]]:
    """Helper to compute mastery for all concepts for a given student."""
    attempts = STUDENT_ATTEMPTS_DB.get(student_id, [])
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
    
    # If student is already strong (>= 0.5), no recommendation needed
    if current_mastery is not None and current_mastery >= 0.5:
        return RecommendationResponse(
            weak_concept="",
            recommended_concept="",
            reason="Student has mastered the current concept.",
            source={}
        )
        
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

@adaptive_router.post("/documents")
def upload_document(payload: Dict[str, Any] = Body(...)):
    """
    POST /adaptive/documents
    Accepts text / transcript / slide chunks and processes them into structured chunks.
    """
    title = payload.get("title", "Untitled Document")
    doc_type = payload.get("file_type", "transcript")
    content = payload.get("content", [])
    
    if doc_type == "transcript" and isinstance(content, list):
        chunks = DocumentIngestor.ingest_transcript_json(content)
    elif doc_type == "slides" and isinstance(content, list):
        chunks = DocumentIngestor.ingest_slides_data(content)
    elif isinstance(content, str):
        chunks = DocumentIngestor.process_raw_text(content)
    else:
        chunks = []
        
    return {
        "document_id": "doc_" + str(hash(title) % 10000),
        "title": title,
        "file_type": doc_type,
        "status": "processed",
        "chunks_count": len(chunks),
        "sample_chunk": chunks[0].dict() if chunks else None
    }

@adaptive_router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: str):
    """
    GET /adaptive/lessons/{lesson_id}
    Returns metadata for a lesson.
    """
    return {
        "lesson_id": lesson_id,
        "title": "Machine Learning Core Concepts",
        "total_slides": 20,
        "duration_seconds": 900,
        "concepts": list(MOCK_CONCEPTS.values())
    }

@adaptive_router.get("/knowledge-graph/{lesson_id}", response_model=GraphResponse)
def get_knowledge_graph(lesson_id: str):
    """
    GET /adaptive/knowledge-graph/{lesson_id}
    Returns nodes and edges for drawing the Knowledge Graph SVG/Canvas.
    """
    nodes = []
    for cid, info in MOCK_CONCEPTS.items():
        src = MOCK_SOURCE_MAPPING.get(cid, {})
        nodes.append({
            "id": cid,
            "label": info.get("name"),
            "slide": src.get("slide"),
            "start_time": src.get("start_time"),
            "end_time": src.get("end_time")
        })
        
    edges = []
    for target_id, prereqs in MOCK_PREREQUISITES.items():
        for src_id in prereqs:
            edges.append({
                "from": src_id,
                "to": target_id,
                "type": "prerequisite"
            })
            
    return GraphResponse(nodes=nodes, edges=edges)

@adaptive_router.get("/concepts/by-slide/{slide_number}")
def get_concepts_by_slide(slide_number: int):
    """
    GET /adaptive/concepts/by-slide/{slide}
    Source Mapper: Lookup concepts by slide number.
    """
    concepts = source_mapper.get_concepts_by_slide(slide_number)
    return {"slide": slide_number, "concepts": concepts}

@adaptive_router.get("/concepts/by-time/{timestamp_seconds}")
def get_concepts_by_time(timestamp_seconds: float):
    """
    GET /adaptive/concepts/by-time/{timestamp}
    Source Mapper: Lookup concept by video timestamp in seconds.
    """
    concept = source_mapper.get_concept_by_time(timestamp_seconds)
    if not concept:
        return {"timestamp": timestamp_seconds, "concept": None, "message": "No concept mapped to this timestamp"}
    return {"timestamp": timestamp_seconds, "concept": concept}

@adaptive_router.post("/quiz/answer")
def submit_quiz_answer(student_id: str, answer: StudentAnswer):
    """
    POST /adaptive/quiz/answer
    Submits a student quiz answer and updates mastery score.
    """
    if student_id not in STUDENT_ATTEMPTS_DB:
        STUDENT_ATTEMPTS_DB[student_id] = []
        
    STUDENT_ATTEMPTS_DB[student_id].append({
        "quiz_id": answer.quiz_id,
        "concept_id": answer.concept_id,
        "is_correct": answer.is_correct,
        "difficulty": answer.difficulty
    })
    
    updated_scores = get_student_mastery_scores(student_id)
    new_mastery = updated_scores.get(answer.concept_id)
    state = compute_mastery_state(new_mastery, is_current=True)
    
    return {
        "student_id": student_id,
        "concept_id": answer.concept_id,
        "new_mastery": new_mastery,
        "mastery_state": state,
        "status": "updated"
    }

@adaptive_router.get("/mastery/{student_id}")
def get_mastery_summary(student_id: str):
    """
    GET /adaptive/mastery/{student_id}
    Returns mastery breakdown and state for each concept.
    """
    scores = get_student_mastery_scores(student_id)
    breakdown = {}
    for cid, score in scores.items():
        state = compute_mastery_state(score)
        breakdown[cid] = {
            "name": MOCK_CONCEPTS.get(cid, {}).get("name"),
            "score": score,
            "state": state
        }
    return {"student_id": student_id, "mastery_summary": breakdown}
