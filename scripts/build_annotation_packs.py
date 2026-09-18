"""Build reviewer-facing source packs without creating ground-truth labels."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STORAGE = ROOT / "data" / "storage.json"
OUT = ROOT / "evals" / "real"
PACKS = OUT / "annotation_packs"

SELECTED = [
    ("lesson_05", "3-Neural_Network.pdf", "PDF: compact neural-network lesson with 26 page chunks."),
    ("lesson_55", "4-Backpropagation.pdf", "PDF: compact backpropagation lesson with 22 page chunks."),
    ("lesson_57", "6-CNN_for_Image_Classification.pdf", "PDF: CNN image-classification lesson with 43 page chunks."),
    ("lesson_59", "YTSave_YouTube_Deep-Learning-What-is-Deep-Learning-Deep_Media_6M5VXKLf4D4_003_480p.mp4", "Video: shorter deep-learning lesson with full timestamp scope."),
    ("lesson_60", "YTSave_YouTube_Machine-Learning-Tutorial-Machine-Learni_Media_G7fPB4OHkys_003_480p.mp4", "Video: long machine-learning lesson sampled at beginning, middle, and end."),
]


def fmt_time(seconds: float | None) -> str:
    if seconds is None:
        return ""
    seconds = int(seconds)
    return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"


def pack_chunks(lesson_id: str, chunks: list[dict]) -> list[dict]:
    if lesson_id != "lesson_60":
        return chunks
    ranges = [(0, 300), (900, 1200), (1794, 2095)]
    return [c for c in chunks if any(start <= float(c.get("start_time") or 0) < end for start, end in ranges)]


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def main() -> None:
    data = json.loads(STORAGE.read_text(encoding="utf-8"))
    docs = data.get("documents", {})
    lessons = data.get("lessons", {})
    chunks_by_lesson: dict[str, list[dict]] = {}
    for chunk in data.get("chunks", []):
        chunks_by_lesson.setdefault(chunk.get("lesson_id"), []).append(chunk)

    selected_rows = []
    concept_rows = []
    grounding_rows = []
    relation_rows = []
    quiz_rows = []
    progress_rows = []
    PACKS.mkdir(parents=True, exist_ok=True)

    for lesson_id, source_name, reason in SELECTED:
        lesson = lessons[lesson_id]
        doc = next((d for d in docs.values() if d.get("lesson_id") == lesson_id), {})
        all_chunks = sorted(chunks_by_lesson.get(lesson_id, []), key=lambda c: (c.get("page") or c.get("start_time") or 0, c.get("chunk_id", "")))
        scoped = pack_chunks(lesson_id, all_chunks)
        is_video = lesson.get("source_type") == "video"
        duration = max((float(c.get("end_time") or 0) for c in all_chunks), default=0)
        selected_rows.append({
            "lesson_id": lesson_id,
            "document_id": doc.get("document_id"),
            "source_type": lesson.get("source_type"),
            "source_group": lesson.get("source_group"),
            "chunk_count": len(all_chunks),
            "page_count": max((int(c.get("page") or c.get("slide") or 0) for c in all_chunks), default=0),
            "duration_seconds": duration,
            "selection_reason": reason,
            "annotation_scope": "full lesson" if len(scoped) == len(all_chunks) else "00:00-05:00; 15:00-20:00; final 05:00 window",
        })
        overview = " ".join((c.get("text") or "").replace("\n", " ") for c in all_chunks[:2])[:700]
        lines = [
            f"# Annotation Pack — {lesson_id}",
            "",
            "## Lesson metadata", "",
            f"- lesson_id: `{lesson_id}`",
            f"- document_id: `{doc.get('document_id')}`",
            f"- source type: `{lesson.get('source_type')}`",
            f"- source file/title: `{source_name}`",
            f"- source_group: `{lesson.get('source_group')}`",
            f"- chunk count: `{len(all_chunks)}`",
            f"- page count OR duration: `{selected_rows[-1]['page_count']} pages`" if not is_video else f"- page count OR duration: `{duration:.2f} seconds`",
            "", "## Source overview", "",
            "**AI-GENERATED ORIENTATION SUMMARY — NOT GROUND TRUTH**", "",
            overview or "No orientation text available.",
            "", "## Source sections", "",
        ]
        if is_video:
            groups: dict[str, list[dict]] = {}
            for chunk in scoped:
                start = float(chunk.get("start_time") or 0)
                if lesson_id == "lesson_60":
                    key = "00:00–05:00" if start < 300 else ("15:00–20:00" if start < 1200 else "Final 05:00 window")
                else:
                    key = f"{fmt_time(start)}–{fmt_time(chunk.get('end_time'))}"
                groups.setdefault(key, []).append(chunk)
            for key, group in groups.items():
                lines += [f"### {key}", "", "Chunk IDs:", *[f"- `{c['chunk_id']}`" for c in group], "", "Transcript:", "", *[(c.get("text") or "").strip() for c in group], ""]
        else:
            for chunk in scoped:
                lines += [f"### Page {chunk.get('page')}", "", "Chunk IDs:", f"- `{chunk['chunk_id']}`", "", "Text:", "", (chunk.get("text") or "").strip(), ""]
        lines += [
            "## Concept Annotation", "",
            "| Human Concept ID | Concept Label | Should Extract? | Evidence Chunk ID | Page/Timestamp | Reviewer Notes |",
            "|---|---|---|---|---|---|", "| | | | | | |", "",
            "Annotate meaningful teachable concepts: principles, methods, processes, important objects, algorithms, theories, dependencies, and major learning ideas. Do not label every noun, speaker names, filenames, ads, or incidental examples. Target approximately 8–12 concepts, without forcing the count.",
            "", "## Relation Annotation", "",
            "| Source Concept | Target Concept | Relation Type | Evidence Chunk ID | Page/Timestamp | Valid? | Notes |",
            "|---|---|---|---|---|---|---|", "| | | | | | | |", "",
            "Use only controlled relation types from the project specification. Include positive relations and useful invalid candidates; do not infer a relation from co-occurrence alone.",
            "", "## Grounding Annotation", "",
            "| Case ID | Claim | Evidence Chunk ID | Page/Timestamp | Support: YES/PARTIAL/NO | Notes |",
            "|---|---|---|---|---|---|", "| | | | | |", "",
            "YES means direct support, PARTIAL means only part of the claim is supported, and NO means the evidence does not support it. Keyword overlap is not enough.",
            "", "## Quiz Case Annotation", "",
            "| Quiz Case ID | Concept | Requested Difficulty | Expected Decision | Evidence Chunk ID | Notes |",
            "|---|---|---|---|---|---|", "| | | | | |", "",
            "Use only GENERATE_QUIZ, DISAMBIGUATE, or REFUSE_UNGROUNDED. Design a mix of supported, ambiguous, insufficient, unsupported, wrong-source, cross-concept, and adversarial cases. Do not force hard questions where the source does not support them.",
        ]
        (PACKS / f"{lesson_id}_annotation_pack.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        for chunk in scoped:
            location = str(chunk.get("page") or f"{fmt_time(chunk.get('start_time'))}-{fmt_time(chunk.get('end_time'))}")
            concept_rows.append([lesson_id, doc.get("document_id", ""), "", "", "", chunk.get("chunk_id", ""), str(chunk.get("page") or ""), location, "", ""])
            grounding_rows.append(["", lesson_id, doc.get("document_id", ""), "", chunk.get("chunk_id", ""), str(chunk.get("page") or ""), str(chunk.get("slide") or ""), str(chunk.get("start_time") or ""), str(chunk.get("end_time") or ""), "", "", "", ""])
        relation_rows.append([lesson_id, "", "", "", "", "", "", "", "", ""])
        quiz_rows.append(["", lesson_id, doc.get("document_id", ""), "", "", "", "", "", "", "", ""])
        progress_rows.append([lesson_id, "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "", "", ""])

    (OUT / "selected_lessons.json").write_text(json.dumps(selected_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(OUT / "concepts.csv", ["lesson_id", "document_id", "concept_id", "concept_label", "should_extract", "evidence_chunk_id", "page", "notes", "reviewer", "review_status"], concept_rows)
    write_csv(OUT / "grounding.csv", ["case_id", "lesson_id", "document_id", "claim", "source_chunk_id", "page", "slide", "start_time", "end_time", "support", "notes", "reviewer", "review_status"], grounding_rows)
    write_csv(OUT / "relations.csv", ["lesson_id", "source_concept", "target_concept", "relation", "evidence_chunk_id", "page", "valid", "notes", "reviewer", "review_status"], relation_rows)
    write_csv(OUT / "quiz_cases.csv", ["quiz_id", "lesson_id", "document_id", "concept_id", "requested_difficulty", "expected_decision", "evidence_chunk_id", "page", "reviewer", "review_status", "notes"], quiz_rows)
    write_csv(OUT / "annotation_progress.csv", ["lesson_id", "concepts_status", "relations_status", "grounding_status", "quiz_cases_status", "reviewer", "review_date", "notes"], progress_rows)


if __name__ == "__main__":
    main()
