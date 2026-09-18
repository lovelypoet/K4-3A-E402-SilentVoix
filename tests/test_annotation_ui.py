import csv
import json

from fastapi.testclient import TestClient

import annotation_api
from main import app


def _setup_annotation_files(tmp_path, monkeypatch):
    real = tmp_path / "real"
    prelabels = real / "prelabels"
    prelabels.mkdir(parents=True)
    gold = {}
    headers = {
        "concepts": ["lesson_id", "document_id", "concept_id", "concept_label", "should_extract", "evidence_chunk_id", "page", "notes", "reviewer", "review_status"],
        "relations": ["lesson_id", "source_concept", "target_concept", "relation", "evidence_chunk_id", "page", "valid", "notes", "reviewer", "review_status"],
        "grounding": ["case_id", "lesson_id", "document_id", "claim", "source_chunk_id", "page", "slide", "start_time", "end_time", "support", "notes", "reviewer", "review_status"],
        "quiz": ["quiz_id", "lesson_id", "document_id", "concept_id", "requested_difficulty", "expected_decision", "evidence_chunk_id", "page", "reviewer", "review_status", "notes"],
    }
    for mode, fields in headers.items():
        path = real / f"{mode if mode != 'quiz' else 'quiz_cases'}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=fields).writeheader()
        gold[mode] = path
    (prelabels / "lesson_x.json").write_text(json.dumps({"concepts": [{"item_id": "c1", "concept_id": "c1", "candidate_label": "Test concept", "evidence_chunk_id": "chunk1", "page": 1, "excerpt": "Evidence"}], "relations": [], "grounding": [], "quiz": []}), encoding="utf-8")
    monkeypatch.setattr(annotation_api, "REAL", real)
    monkeypatch.setattr(annotation_api, "PRELABELS", prelabels)
    monkeypatch.setattr(annotation_api, "GOLD_FILES", gold)
    monkeypatch.setattr(annotation_api, "SESSION", real / "reviewer_session.json")


def test_annotation_accept_writes_human_approved(tmp_path, monkeypatch):
    _setup_annotation_files(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.post("/annotation/api/review", json={"lesson_id": "lesson_x", "mode": "concepts", "item_id": "c1", "decision": "ACCEPT", "reviewer": "reviewer-1", "role": "DOMAIN_EXPERT"})
    assert response.status_code == 200
    text = annotation_api.GOLD_FILES["concepts"].read_text(encoding="utf-8")
    assert "HUMAN_APPROVED" in text
    assert "AI_PRELABEL_HUMAN_APPROVED" in text


def test_annotation_skip_does_not_write_label(tmp_path, monkeypatch):
    _setup_annotation_files(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.post("/annotation/api/review", json={"lesson_id": "lesson_x", "mode": "concepts", "item_id": "c1", "decision": "SKIP", "reviewer": "reviewer-1", "role": "DOMAIN_EXPERT"})
    assert response.status_code == 200
    assert "HUMAN_APPROVED" not in annotation_api.GOLD_FILES["concepts"].read_text(encoding="utf-8")


def test_annotation_requires_reviewer_identity(tmp_path, monkeypatch):
    _setup_annotation_files(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.post("/annotation/api/review", json={"lesson_id": "lesson_x", "mode": "concepts", "item_id": "c1", "decision": "ACCEPT", "reviewer": "", "role": "DOMAIN_EXPERT"})
    assert response.status_code == 400
