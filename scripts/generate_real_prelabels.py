"""Generate reviewable AI suggestions, never human labels."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai.pipeline import build_graph, generate_quiz

STORAGE = ROOT / "data" / "storage.json"
OUT = ROOT / "evals" / "real" / "prelabels"
LESSONS = ["lesson_05", "lesson_55", "lesson_57", "lesson_59", "lesson_60"]


def scope(lesson_id: str, chunks: list[dict]) -> list[dict]:
    if lesson_id != "lesson_60":
        return chunks
    return [c for c in chunks if any(start <= float(c.get("start_time") or 0) < end for start, end in [(0, 300), (900, 1200), (1794, 2095)])]


def main() -> None:
    data = json.loads(STORAGE.read_text(encoding="utf-8"))
    for lesson_id in LESSONS:
        raw = [c for c in data.get("chunks", []) if c.get("lesson_id") == lesson_id]
        chunks = scope(lesson_id, raw)
        ai_chunks = [{"chunk_id": c["chunk_id"], "document_id": c.get("document_id"), "text": c.get("text", ""), "source": {"page": c.get("page"), "slide": c.get("slide"), "start_time": c.get("start_time"), "end_time": c.get("end_time")}} for c in chunks]
        graph = build_graph(ai_chunks, lesson_id=lesson_id)
        by_id = {c["chunk_id"]: c for c in chunks}
        concepts = []
        for node in graph.get("nodes", [])[:15]:
            source = (node.get("sources") or [{}])[0]
            chunk = by_id.get(source.get("chunk_id"), {})
            concepts.append({"item_id": f"concept_{node['id']}", "concept_id": node["id"], "candidate_label": node.get("label", ""), "evidence_chunk_id": source.get("chunk_id", ""), "page": chunk.get("page", ""), "excerpt": chunk.get("text", "")[:500], "confidence": "MEDIUM", "origin": "AI_PRELABEL", "human_status": "UNREVIEWED", "document_id": chunk.get("document_id", "")})
        relations = []
        for idx, edge in enumerate(graph.get("edges", [])[:10], 1):
            evidence = edge.get("evidence") or {}
            chunk = by_id.get(evidence.get("chunk_id"), {})
            relations.append({"item_id": f"relation_{idx}", "source_concept": edge.get("source", ""), "target_concept": edge.get("target", ""), "relation": edge.get("relation", "related_to"), "evidence_chunk_id": evidence.get("chunk_id", ""), "page": chunk.get("page", ""), "excerpt": chunk.get("text", "")[:500], "confidence": "MEDIUM", "origin": "AI_PRELABEL", "human_status": "UNREVIEWED", "document_id": chunk.get("document_id", "")})
        grounding = []
        for idx, chunk in enumerate(chunks[:10], 1):
            grounding.append({"item_id": f"grounding_{idx}", "claim": (chunk.get("text") or "")[:300], "evidence_chunk_id": chunk.get("chunk_id", ""), "page": chunk.get("page", ""), "excerpt": chunk.get("text", "")[:500], "origin": "AI_PRELABEL", "human_status": "UNREVIEWED", "document_id": chunk.get("document_id", "")})
        quiz_cases = []
        for idx, node in enumerate(graph.get("nodes", [])[:8], 1):
            try:
                quiz = generate_quiz(graph, node["id"], difficulty="medium")
                source = (node.get("sources") or [{}])[0]
                chunk = by_id.get(source.get("chunk_id"), {})
                quiz_cases.append({"item_id": f"quiz_{idx}", "concept_id": node["id"], "requested_difficulty": "MEDIUM", "expected_decision": quiz.get("decision", "DISAMBIGUATE"), "evidence_chunk_id": source.get("chunk_id", ""), "page": chunk.get("page", ""), "excerpt": chunk.get("text", "")[:500], "origin": "AI_PRELABEL", "human_status": "UNREVIEWED", "document_id": chunk.get("document_id", "")})
            except Exception:
                continue
        result = {"lesson_id": lesson_id, "origin": "AI_PRELABEL", "human_status": "UNREVIEWED", "concepts": concepts, "relations": relations, "grounding": grounding, "quiz": quiz_cases}
        (OUT / f"{lesson_id}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    main()
