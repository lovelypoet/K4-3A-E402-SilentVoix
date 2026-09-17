import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adaptive_learning.models import Document, Chunk, StudentAnswer, RecommendationResponse
from adaptive_learning.ingestion import DocumentIngestor
from adaptive_learning.source_mapper import SourceMapper
from adaptive_learning.api import (
    upload_file_or_link, 
    get_knowledge_graph, 
    get_concepts_by_slide, 
    get_concepts_by_time, 
    submit_quiz_answer, 
    get_mastery_summary,
    get_recommendation
)

def test_backend_implementation():
    print("========================================")
    print("RUNNING BACKEND MODULE UNIT TESTS")
    print("========================================")
    
    # 1. Test Ingestion & Chunking
    print("[1/5] Testing Ingestion & Chunk Metadata Preservation...")
    transcript_sample = [
        {"start_time": 0, "end_time": 120, "text": "Welcome to ML Basics."},
        {"start_time": 121, "end_time": 300, "text": "Supervised learning overview."}
    ]
    chunks = DocumentIngestor.ingest_transcript_json(transcript_sample, lesson_id="l1")
    assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
    assert chunks[0].start_time == 0 and chunks[0].end_time == 120, "Timestamp metadata mismatch!"
    
    slides_sample = [
        {"slide": 1, "text": "Slide 1 Content"},
        {"slide": 20, "text": "Gradient Descent Slide"}
    ]
    slide_chunks = DocumentIngestor.ingest_slides_data(slides_sample, lesson_id="l1")
    assert len(slide_chunks) == 2, f"Expected 2 slide chunks, got {len(slide_chunks)}"
    assert slide_chunks[1].slide == 20, "Slide metadata mismatch!"
    print("  -> Passed Ingestion & Chunking tests!")

    # 2. Test Source Mapper
    print("[2/5] Testing Source Mapper Engine (2-Way Lookups)...")
    mapper = SourceMapper()
    
    # Slide 20 lookup
    concepts_slide_20 = mapper.get_concepts_by_slide(20)
    assert len(concepts_slide_20) == 1, f"Expected 1 concept for slide 20, got {len(concepts_slide_20)}"
    assert concepts_slide_20[0]["concept_id"] == "c6", f"Expected c6, got {concepts_slide_20[0]['concept_id']}"
    assert concepts_slide_20[0]["name"] == "Gradient Descent"
    
    # Timestamp 755 (12m35s) lookup
    concept_time = mapper.get_concept_by_time(755.0)
    assert concept_time is not None, "Expected concept at t=755s"
    assert concept_time["concept_id"] == "c6", f"Expected c6 at 755s, got {concept_time['concept_id']}"
    
    # Reverse lookup
    source_c5 = mapper.get_source_by_concept("c5")
    assert source_c5.get("slide") == 17, f"Expected slide 17 for c5, got {source_c5.get('slide')}"
    print("  -> Passed Source Mapper tests!")

    # 3. Test Knowledge Graph API Endpoint
    print("[3/5] Testing Knowledge Graph Endpoint...")
    graph = get_knowledge_graph("lesson_01")
    assert len(graph.nodes) == 6, f"Expected 6 nodes, got {len(graph.nodes)}"
    assert len(graph.edges) == 5, f"Expected 5 edges, got {len(graph.edges)}"
    print("  -> Passed Knowledge Graph API test!")

    # 4. Test Quiz Submission & Mastery Update
    print("[4/5] Testing Quiz Answer & Mastery Update Endpoint...")
    ans = StudentAnswer(quiz_id="q_test", concept_id="c6", is_correct=True, difficulty=1.0)
    res = submit_quiz_answer(student_id="student_test_user", answer=ans)
    assert res["status"] == "updated"
    assert res["new_mastery"] == 1.0, f"Expected mastery 1.0, got {res['new_mastery']}"
    
    summary = get_mastery_summary("student_test_user")
    assert summary["mastery_summary"]["c6"]["state"] == "mastered"
    print("  -> Passed Quiz Submission & Mastery test!")

    # 5. Test Adaptive Recommendation Flow
    print("[5/5] Testing Adaptive Recommendation Endpoint...")
    rec = get_recommendation(student_id="student_1", current_concept_id="c6")
    assert rec.recommended_concept == "Loss Function", f"Expected Loss Function, got {rec.recommended_concept}"
    assert rec.source.get("slide") == 17, f"Expected slide 17, got {rec.source.get('slide')}"
    print("  -> Passed Adaptive Recommendation test!")

    print("========================================")
    print("ALL BACKEND MODULE TESTS PASSED (5/5)!")
    print("========================================")

if __name__ == "__main__":
    test_backend_implementation()
