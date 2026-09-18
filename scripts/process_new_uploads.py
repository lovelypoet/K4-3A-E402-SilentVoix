"""Register and ingest the newly supplied local PDFs/videos.

This is deliberately a local, deterministic runner. It never invents labels,
does not call the network, and records unavailable ASR as a truthful status.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adaptive_learning.ingestion import (
    DocumentIngestor,
    OCR_REQUIRED,
    TRANSCRIPTION_REQUIRED,
    INGESTION_FAILED,
)
from adaptive_learning.storage import StorageManager

UPLOADS = ROOT / "uploads"
STORAGE = ROOT / "data" / "storage.json"
REPORT = ROOT / "validation" / "ingestion" / "new_files_processing.md"
MANIFEST = ROOT / "evals" / "real" / "lesson_manifest.json"
TARGET_PDFS = {
    "3-Neural_Network.pdf",
    "4-Backpropagation.pdf",
    "5-Convolutional_Neural_Network.pdf",
    "6-CNN_for_Image_Classification.pdf",
    "7-Object_Detection_and_Image_Segmentation.pdf",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def existing_by_source(data: dict[str, Any], source_key: str) -> dict[str, Any] | None:
    for lesson in data.get("lessons", {}).values():
        if lesson.get("source_key") == source_key:
            return lesson
    for doc in data.get("documents", {}).values():
        if doc.get("source_key") == source_key:
            return {
                "lesson_id": doc.get("lesson_id"),
                "document_id": doc.get("document_id"),
                "source_key": source_key,
            }
    return None


def existing_file_hashes(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for doc in data.get("documents", {}).values():
        raw = str(doc.get("file_path") or "")
        candidates = [Path(raw), UPLOADS / Path(raw).name]
        for candidate in candidates:
            if candidate.is_file():
                try:
                    result[sha256(candidate)] = doc
                except OSError:
                    pass
                break
    return result


def next_id(data: dict[str, Any], key: str, prefix: str) -> str:
    used = set(data.get(key, {}).keys())
    index = 1
    while f"{prefix}_{index:02d}" in used:
        index += 1
    return f"{prefix}_{index:02d}"


def process_file(path: Path, storage: StorageManager) -> dict[str, Any]:
    data = storage.data
    digest = sha256(path)
    source_key = f"file:{digest}"
    source_group = source_key
    duplicate = existing_by_source(data, source_key) or existing_file_hashes(data).get(digest)
    base = {
        "file": path.name,
        "type": path.suffix.lower().lstrip("."),
        "source_key": source_key,
        "duplicate": bool(duplicate),
        "processing_path": "",
        "chunks": 0,
        "metadata": "document_id, lesson_id, source_key, source_group",
        "status": "",
        "notes": "",
    }
    if duplicate:
        base.update(
            status="DUPLICATE_SOURCE",
            notes=f"existing_lesson_id={duplicate.get('lesson_id')}; existing_document_id={duplicate.get('document_id')}",
        )
        return base

    lesson_id = next_id(data, "lessons", "lesson")
    document_id = next_id(data, "documents", "doc")
    ext = path.suffix.lower()
    chunks = []
    error: str | None = None
    if ext == ".pdf":
        base["processing_path"] = "pypdf digital-text extraction"
        try:
            chunks = DocumentIngestor.ingest_pdf_file(str(path), lesson_id=lesson_id)
        except ValueError as exc:
            error = OCR_REQUIRED if OCR_REQUIRED in str(exc) else INGESTION_FAILED
            base["notes"] = str(exc)
    elif ext in {".mp4", ".mov", ".avi", ".webm", ".mkv", ".mp3", ".wav", ".m4a"}:
        base["processing_path"] = "faster-whisper local ASR"
        try:
            chunks = DocumentIngestor.ingest_local_video_file(
                str(path), lesson_id=lesson_id, document_id=document_id, source_key=source_key
            )
        except Exception as exc:
            error = TRANSCRIPTION_REQUIRED if TRANSCRIPTION_REQUIRED in str(exc) else INGESTION_FAILED
            base["notes"] = str(exc)
    else:
        base.update(status="FAILED", notes="Unsupported extension")
        return base

    DocumentIngestor.stamp_chunks(
        chunks,
        document_id=document_id,
        source_key=source_key,
        source_group=source_group,
        source_type="video" if ext != ".pdf" else "document",
    )
    chunk_dicts = [chunk.model_dump() for chunk in chunks]
    if chunks:
        data.setdefault("chunks", []).extend(chunk_dicts)
    title = path.stem
    file_type = "video" if ext != ".pdf" else "pdf"
    status = "READY" if chunks else (error or "FAILED")
    data.setdefault("documents", {})[document_id] = {
        "document_id": document_id,
        "title": title,
        "file_type": file_type,
        "file_path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "lesson_id": lesson_id,
        "chunks_count": len(chunks),
        "source_key": source_key,
        "source_group": source_group,
        "status": status,
        "error_code": error,
    }
    data.setdefault("lessons", {})[lesson_id] = {
        "lesson_id": lesson_id,
        "title": title,
        "file_path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "source_type": "video" if ext != ".pdf" else "document",
        "total_slides": max((c.slide or 0 for c in chunks), default=0),
        "duration_seconds": max((c.end_time or 0 for c in chunks), default=0),
        "source_key": source_key,
        "source_group": source_group,
        "status": status,
        "error_code": error,
    }
    base.update(chunks=len(chunks), status=status)
    return base


def main() -> None:
    storage = StorageManager(str(STORAGE))
    files = [p for p in UPLOADS.iterdir() if p.is_file() and (p.suffix.lower() in {".mp4", ".mov", ".avi", ".webm", ".mkv", ".mp3", ".wav", ".m4a"} or p.name in TARGET_PDFS)]
    files = sorted(files, key=lambda p: p.name.lower())
    results = [process_file(path, storage) for path in files]
    storage.save()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# New Files Processing Report",
        "",
        "Generated by `scripts/process_new_uploads.py`. Exact file SHA-256 is the local source identity.",
        "",
        "| File | Type | Duplicate? | Processing Path | Chunks | Metadata | Status | Notes |",
        "|---|---|---:|---|---:|---|---|---|",
    ]
    for row in results:
        notes = row["notes"].replace("|", "\\|")
        lines.append(f"| {row['file']} | {row['type']} | {'YES' if row['duplicate'] else 'NO'} | {row['processing_path']} | {row['chunks']} | {row['metadata']} | {row['status']} | {notes} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Keep the manifest source-of-truth format compatible with the existing audit.
    manifest = []
    for lesson in storage.data.get("lessons", {}).values():
        lesson_chunks = [c for c in storage.data.get("chunks", []) if c.get("lesson_id") == lesson.get("lesson_id")]
        if not lesson_chunks:
            continue
        docs = [d for d in storage.data.get("documents", {}).values() if d.get("lesson_id") == lesson.get("lesson_id")]
        doc = docs[0] if docs else {}
        source_type = lesson.get("source_type") or doc.get("file_type") or "unknown"
        valid_metadata = all(c.get("document_id") and c.get("lesson_id") and c.get("source_group") for c in lesson_chunks)
        manifest.append({
            "lesson_id": lesson.get("lesson_id"),
            "document_id": doc.get("document_id"),
            "source_group": lesson.get("source_group"),
            "source_type": source_type,
            "source_path_or_reference": lesson.get("file_path") or lesson.get("video_url") or lesson.get("slide_url"),
            "chunk_count": len(lesson_chunks),
            "page_count_or_slide_count": max((c.get("page") or c.get("slide") or 0 for c in lesson_chunks), default=0),
            "duration_seconds": max((c.get("end_time") or 0 for c in lesson_chunks), default=0),
            "ingestion_status": lesson.get("status"),
            "selected_for_real_eval": bool(valid_metadata and lesson.get("status") == "READY"),
            "reason": "Ready for human annotation; no auto-labels created." if valid_metadata and lesson.get("status") == "READY" else "Needs ingestion repair or human source verification.",
        })
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
