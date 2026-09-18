from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
REAL = ROOT / "evals" / "real"
PRELABELS = REAL / "prelabels"
STORAGE = ROOT / "data" / "storage.json"
SESSION = REAL / "reviewer_session.json"
GOLD_FILES = {
    "concepts": REAL / "concepts.csv",
    "relations": REAL / "relations.csv",
    "grounding": REAL / "grounding.csv",
    "quiz": REAL / "quiz_cases.csv",
}

router = APIRouter(prefix="/annotation/api", tags=["Local Annotation"])


class ReviewRequest(BaseModel):
    lesson_id: str
    mode: str
    item_id: str
    decision: str
    reviewer: str
    role: str
    edited_label: str | None = None
    edited_relation: str | None = None
    notes: str | None = None
    evidence_chunk_id: str | None = None
    page: str | None = None


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f"{path.stem}_", suffix=".csv", dir=path.parent)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _session(req: ReviewRequest) -> None:
    if not req.reviewer.strip() or req.role not in {"TEAM_MEMBER", "LECTURER", "STUDENT", "DOMAIN_EXPERT"}:
        raise HTTPException(status_code=400, detail="Reviewer identity and valid role are required.")
    SESSION.write_text(json.dumps({"reviewer": req.reviewer.strip(), "role": req.role}, indent=2), encoding="utf-8")


def _item(lesson_id: str, mode: str, item_id: str) -> dict[str, Any]:
    data = _load_json(PRELABELS / f"{lesson_id}.json", {})
    for item in data.get(mode, []):
        if item.get("item_id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Prelabel item not found")


def _append_review(req: ReviewRequest, item: dict[str, Any]) -> None:
    mode = req.mode
    path = GOLD_FILES[mode]
    fields, rows = _read_csv(path)
    extra = ["origin", "review_timestamp"]
    fields = fields or {
        "concepts": ["lesson_id", "document_id", "concept_id", "concept_label", "should_extract", "evidence_chunk_id", "page", "notes", "reviewer", "review_status"],
        "relations": ["lesson_id", "source_concept", "target_concept", "relation", "evidence_chunk_id", "page", "valid", "notes", "reviewer", "review_status"],
        "grounding": ["case_id", "lesson_id", "document_id", "claim", "source_chunk_id", "page", "slide", "start_time", "end_time", "support", "notes", "reviewer", "review_status"],
        "quiz": ["quiz_id", "lesson_id", "document_id", "concept_id", "requested_difficulty", "expected_decision", "evidence_chunk_id", "page", "reviewer", "review_status", "notes"],
    }[mode]
    for field in extra:
        if field not in fields:
            fields.append(field)

    status = "HUMAN_APPROVED" if req.decision in {"ACCEPT", "VALID", "YES", "PARTIAL", "GENERATE_QUIZ", "DISAMBIGUATE", "REFUSE_UNGROUNDED", "ADD_NEW"} else "HUMAN_REJECTED"
    row: dict[str, Any] = {field: "" for field in fields}
    row.update({"reviewer": req.reviewer, "review_status": status, "origin": "HUMAN" if req.decision == "ADD_NEW" else "AI_PRELABEL_HUMAN_APPROVED", "review_timestamp": _now(), "notes": req.notes or ""})
    if mode == "concepts":
        row.update({"lesson_id": req.lesson_id, "document_id": item.get("document_id", ""), "concept_id": item.get("concept_id", req.item_id), "concept_label": req.edited_label or item.get("candidate_label", ""), "should_extract": "TRUE" if status == "HUMAN_APPROVED" else "FALSE", "evidence_chunk_id": req.evidence_chunk_id or item.get("evidence_chunk_id", ""), "page": req.page or item.get("page", "")})
    elif mode == "relations":
        row.update({"lesson_id": req.lesson_id, "source_concept": item.get("source_concept", ""), "target_concept": item.get("target_concept", ""), "relation": req.edited_relation or item.get("relation", ""), "evidence_chunk_id": item.get("evidence_chunk_id", ""), "page": item.get("page", ""), "valid": "TRUE" if req.decision == "VALID" else "FALSE"})
    elif mode == "grounding":
        row.update({"case_id": req.item_id, "lesson_id": req.lesson_id, "document_id": item.get("document_id", ""), "claim": item.get("claim", ""), "source_chunk_id": item.get("evidence_chunk_id", ""), "page": item.get("page", ""), "support": req.decision})
    else:
        row.update({"quiz_id": req.item_id, "lesson_id": req.lesson_id, "document_id": item.get("document_id", ""), "concept_id": item.get("concept_id", ""), "requested_difficulty": item.get("requested_difficulty", ""), "expected_decision": req.decision, "evidence_chunk_id": item.get("evidence_chunk_id", ""), "page": item.get("page", "")})
    _atomic_csv(path, fields, rows + [row])


@router.get("/lessons")
def annotation_lessons():
    selected = _load_json(REAL / "selected_lessons.json", [])
    result = []
    for lesson in selected:
        counts = {}
        for mode in GOLD_FILES:
            _, rows = _read_csv(GOLD_FILES[mode])
            counts[mode] = sum(1 for row in rows if row.get("lesson_id") == lesson["lesson_id"] and row.get("review_status") in {"HUMAN_APPROVED", "HUMAN_REJECTED"})
        result.append({**lesson, "progress": counts})
    return result


@router.get("/items/{lesson_id}/{mode}")
def annotation_items(lesson_id: str, mode: str):
    if mode not in GOLD_FILES:
        raise HTTPException(status_code=400, detail="Unknown annotation mode")
    return _load_json(PRELABELS / f"{lesson_id}.json", {}).get(mode, [])


@router.get("/source/{lesson_id}")
def annotation_source(lesson_id: str):
    storage = _load_json(STORAGE, {})
    return [chunk for chunk in storage.get("chunks", []) if chunk.get("lesson_id") == lesson_id]


@router.post("/review")
def save_review(req: ReviewRequest):
    if req.mode not in GOLD_FILES:
        raise HTTPException(status_code=400, detail="Unknown annotation mode")
    if req.decision == "SKIP":
        return {"status": "skipped", "message": "Skipped; no gold label written."}
    item = {} if req.decision == "ADD_NEW" else _item(req.lesson_id, req.mode, req.item_id)
    _session(req)
    _append_review(req, item)
    return {"status": "saved", "review_status": "HUMAN_APPROVED" if req.decision not in {"REJECT", "INVALID", "NO"} else "HUMAN_REJECTED"}


@router.get("/summary")
def annotation_summary():
    result = {"concepts_approved": 0, "concepts_rejected": 0, "relations_valid": 0, "relations_invalid": 0, "grounding_yes": 0, "grounding_partial": 0, "grounding_no": 0, "quiz_generate": 0, "quiz_disambiguate": 0, "quiz_refuse": 0, "unresolved": 0}
    _, concepts = _read_csv(GOLD_FILES["concepts"])
    _, relations = _read_csv(GOLD_FILES["relations"])
    _, grounding = _read_csv(GOLD_FILES["grounding"])
    _, quizzes = _read_csv(GOLD_FILES["quiz"])
    result["concepts_approved"] = sum(r.get("review_status") == "HUMAN_APPROVED" for r in concepts)
    result["concepts_rejected"] = sum(r.get("review_status") == "HUMAN_REJECTED" for r in concepts)
    result["relations_valid"] = sum(r.get("valid") == "TRUE" for r in relations)
    result["relations_invalid"] = sum(r.get("valid") == "FALSE" for r in relations)
    result["grounding_yes"] = sum(r.get("support") == "YES" for r in grounding)
    result["grounding_partial"] = sum(r.get("support") == "PARTIAL" for r in grounding)
    result["grounding_no"] = sum(r.get("support") == "NO" for r in grounding)
    result["quiz_generate"] = sum(r.get("expected_decision") == "GENERATE_QUIZ" for r in quizzes)
    result["quiz_disambiguate"] = sum(r.get("expected_decision") == "DISAMBIGUATE" for r in quizzes)
    result["quiz_refuse"] = sum(r.get("expected_decision") == "REFUSE_UNGROUNDED" for r in quizzes)
    result["unresolved"] = sum(r.get("review_status") in {"NEEDS_ADJUDICATION", "UNREVIEWED"} for r in concepts + relations + grounding + quizzes)
    return result


@router.post("/export")
def export_summary():
    summary = annotation_summary()
    out = ROOT / "validation" / "human_review" / "human_labeling_summary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Human Labeling Summary", "", "This is an annotation-progress report, not a model evaluation report.", "", "```json", json.dumps(summary, indent=2), "```", "", "Human reviewers and labels remain subject to explicit confirmation."]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": "exported", "path": str(out.relative_to(ROOT))}


def annotation_page() -> HTMLResponse:
    page = (ROOT / "fe" / "annotation.html").read_text(encoding="utf-8")
    return HTMLResponse(page)
