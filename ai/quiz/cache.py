from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CACHE_FILE = Path(__file__).resolve().parents[2] / "data" / "quiz_cache.json"
PROMPT_VERSION = "grounded_quiz_v4_short_output"


def source_content_hash(evidence: list[dict[str, Any]]) -> str:
    payload = [
        {
            "chunk_id": item.get("chunk_id"),
            "text": str(item.get("text") or ""),
            "page": item.get("page"), "slide": item.get("slide"),
            "start_time": item.get("start_time"), "end_time": item.get("end_time"),
        }
        for item in evidence
    ]
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_cache_key(lesson_id: str, concept_id: str, difficulty: str, source_hash: str, provider: str, model: str, prompt_version: str = PROMPT_VERSION) -> str:
    values = [lesson_id, concept_id, difficulty, source_hash, prompt_version, provider, model]
    return hashlib.sha256("|".join(values).encode("utf-8")).hexdigest()


class QuizCache:
    def __init__(self, path: str | Path = DEFAULT_CACHE_FILE):
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def get(self, key: str) -> dict[str, Any] | None:
        item = self._read().get(key)
        if not item or item.get("validation_result", {}).get("passed") is not True:
            return None
        return item.get("quiz")

    def put(self, key: str, quiz: dict[str, Any], *, source_hash: str, provider: str, model: str, prompt_version: str = PROMPT_VERSION) -> None:
        data = self._read()
        data[key] = {
            "quiz": quiz,
            "citations": quiz.get("citations", []),
            "generator": quiz.get("generator_type"),
            "model": model,
            "provider": provider,
            "prompt_version": prompt_version,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_hash": source_hash,
            "validation_result": quiz.get("validation", {}),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(prefix="quiz_cache_", suffix=".json", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
