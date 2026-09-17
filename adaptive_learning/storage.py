import os
import json
from typing import Dict, List, Any, Optional
from .mock_data import MOCK_CONCEPTS, MOCK_PREREQUISITES, MOCK_SOURCE_MAPPING, MOCK_STUDENT_ATTEMPTS

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STORAGE_FILE = os.path.join(STORAGE_DIR, "storage.json")

class StorageManager:
    """
    Manages persistent JSON storage for Documents, Lessons, Chunks, Quizzes, and Student Attempts.
    Ensures data persists across FastAPI server restarts.
    """
    def __init__(self, filepath: str = STORAGE_FILE):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.data: Dict[str, Any] = {
            "documents": {},
            "lessons": {
                "lesson_01": {
                    "lesson_id": "lesson_01",
                    "title": "Machine Learning Core Concepts",
                    "video_url": "https://www.youtube.com/watch?v=aircAruvnKk",
                    "slide_url": None,
                    "file_path": None,
                    "total_slides": 20,
                    "duration_seconds": 900
                }
            },
            "chunks": [],
            "concepts": dict(MOCK_CONCEPTS),
            "prerequisites": dict(MOCK_PREREQUISITES),
            "source_mappings": dict(MOCK_SOURCE_MAPPING),
            "student_attempts": dict(MOCK_STUDENT_ATTEMPTS)
        }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                    for key in self.data:
                        if key in saved_data:
                            self.data[key] = saved_data[key]
            except Exception as e:
                print(f"[StorageManager] Error loading storage: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[StorageManager] Error saving storage: {e}")

    # --- Student Attempts ---
    def get_student_attempts(self, student_id: str) -> List[Dict[str, Any]]:
        return self.data["student_attempts"].get(student_id, [])

    def add_student_attempt(self, student_id: str, attempt: Dict[str, Any]):
        if student_id not in self.data["student_attempts"]:
            self.data["student_attempts"][student_id] = []
        self.data["student_attempts"][student_id].append(attempt)
        self.save()

    # --- Documents & Lessons ---
    def save_document(self, doc_data: Dict[str, Any]):
        doc_id = doc_data.get("document_id")
        if doc_id:
            self.data["documents"][doc_id] = doc_data
            self.save()

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.data["documents"].get(doc_id)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return list(self.data["documents"].values())

    def save_lesson(self, lesson_data: Dict[str, Any]):
        lesson_id = lesson_data.get("lesson_id")
        if lesson_id:
            self.data["lessons"][lesson_id] = lesson_data
            self.save()

    def get_lesson(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        return self.data["lessons"].get(lesson_id)

    def get_all_lessons(self) -> List[Dict[str, Any]]:
        return list(self.data["lessons"].values())

    def get_next_lesson_id(self) -> str:
        count = len(self.data["lessons"]) + 1
        new_id = f"lesson_{count:02d}"
        while new_id in self.data["lessons"]:
            count += 1
            new_id = f"lesson_{count:02d}"
        return new_id

    def get_next_document_id(self) -> str:
        count = len(self.data["documents"]) + 1
        new_id = f"doc_{count:02d}"
        while new_id in self.data["documents"]:
            count += 1
            new_id = f"doc_{count:02d}"
        return new_id

    def get_next_quiz_id(self) -> str:
        count = len(self.data.get("quizzes", {})) + 1
        return f"quiz_{count:02d}"

    def get_next_concept_id(self) -> str:
        count = len(self.data.get("concepts", {})) + 1
        new_id = f"c{count}"
        while new_id in self.data.get("concepts", {}):
            count += 1
            new_id = f"c{count}"
        return new_id

    # --- Chunks & Slides ---
    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        self.data["chunks"].extend(new_chunks)
        self.save()

    def replace_chunks_for_lesson(self, lesson_id: str, new_chunks: List[Dict[str, Any]]):
        """Xóa toàn bộ chunks cũ của lesson rồi ghi chunks mới (tránh trùng khi re-upload)."""
        self.data["chunks"] = [c for c in self.data["chunks"] if c.get("lesson_id") != lesson_id]
        self.data["chunks"].extend(new_chunks)
        self.save()

    def get_chunks_by_lesson(self, lesson_id: str) -> List[Dict[str, Any]]:
        return [c for c in self.data["chunks"] if c.get("lesson_id") == lesson_id]

    def get_slides_by_lesson(self, lesson_id: str) -> List[Dict[str, Any]]:
        chunks = self.get_chunks_by_lesson(lesson_id)
        slides_dict = {}
        for c in chunks:
            slide_num = c.get("slide")
            if slide_num is not None:
                if slide_num not in slides_dict:
                    slides_dict[slide_num] = []
                slides_dict[slide_num].append(c.get("text", ""))
        
        result = []
        for slide_num in sorted(slides_dict.keys()):
            result.append({
                "slide": slide_num,
                "text": "\n\n".join(slides_dict[slide_num])
            })
        return result

    def get_transcript_by_lesson(self, lesson_id: str) -> List[Dict[str, Any]]:
        chunks = self.get_chunks_by_lesson(lesson_id)
        transcript = []
        for c in chunks:
            if c.get("start_time") is not None and c.get("end_time") is not None:
                transcript.append({
                    "chunk_id": c.get("chunk_id"),
                    "start_time": c.get("start_time"),
                    "end_time": c.get("end_time"),
                    "text": c.get("text")
                })
        return sorted(transcript, key=lambda x: x["start_time"])

    def get_concepts_by_lesson(self, lesson_id: str) -> List[Dict[str, Any]]:
        """
        Chỉ trả concepts thuộc đúng lesson_id.
        Không dùng time-range để “đoán” — tránh dính mock c1..c6 vào bài YouTube khác.
        """
        matched_concepts = []
        seen = set()
        concepts = self.data.get("concepts", {})
        mappings = self.data.get("source_mappings", {})

        for cid, cinfo in concepts.items():
            name = cinfo.get("name", "") or ""
            if name.startswith("Mốc ") or name.startswith("Trang Slide "):
                continue

            src = mappings.get(cid, {})
            concept_lesson = cinfo.get("lesson_id") or src.get("lesson_id")

            # Legacy mock không gắn lesson → chỉ thuộc lesson_01
            if concept_lesson is None and cid in {"c1", "c2", "c3", "c4", "c5", "c6"}:
                concept_lesson = "lesson_01"

            if concept_lesson == lesson_id and cid not in seen:
                seen.add(cid)
                out = dict(cinfo)
                out.setdefault("concept_id", cid)
                out.setdefault("lesson_id", lesson_id)
                matched_concepts.append(out)

        return matched_concepts

db_storage = StorageManager()
