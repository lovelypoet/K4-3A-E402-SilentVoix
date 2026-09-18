"""Run local ASR and persist timestamped chunks for registered video records."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adaptive_learning.ingestion import DocumentIngestor
from adaptive_learning.storage import StorageManager


def main() -> None:
    storage = StorageManager(str(ROOT / "data" / "storage.json"))
    only_document = os.getenv("VIDEO_DOCUMENT_ID")
    for document in list(storage.data.get("documents", {}).values()):
        if document.get("file_type") != "video" or document.get("status") == "READY":
            continue
        if only_document and document.get("document_id") != only_document:
            continue
        path = ROOT / str(document.get("file_path", "")).replace("/", os.sep)
        lesson_id = document.get("lesson_id")
        if not lesson_id or not path.is_file():
            continue
        print(f"Transcribing {path.name} with WHISPER_MODEL={os.getenv('WHISPER_MODEL', 'small')}")
        chunks = DocumentIngestor.ingest_local_video_file(
            str(path),
            lesson_id=lesson_id,
            document_id=document["document_id"],
            source_key=document.get("source_key"),
        )
        storage.replace_chunks_for_lesson(lesson_id, [chunk.model_dump() for chunk in chunks])
        document["chunks_count"] = len(chunks)
        document["status"] = "READY"
        document["error_code"] = None
        lesson = storage.data.get("lessons", {}).get(lesson_id, {})
        lesson["status"] = "READY"
        lesson["error_code"] = None
        lesson["duration_seconds"] = max((chunk.end_time or 0 for chunk in chunks), default=0.0)
        storage.data["lessons"][lesson_id] = lesson
        storage.save()
        print(f"READY {document['document_id']} {lesson_id}: chunks={len(chunks)} duration={lesson['duration_seconds']}")


if __name__ == "__main__":
    main()
