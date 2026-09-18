from __future__ import annotations

from typing import Any, Dict, List

from ai.extraction.concept_extractor import extract_concepts_from_chunk
from ai.extraction.normalizer import deduplicate_concepts
from ai.extraction.relationship_extractor import extract_relationships


def _merge_sources(concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for concept in concepts:
        key = concept["id"]
        if key not in merged:
            merged[key] = {
                "id": concept["id"],
                "label": concept["label"],
                "description": concept["description"],
                "sources": [],
            }
        source = concept.get("source") or {}
        if source not in merged[key]["sources"]:
            merged[key]["sources"].append({
                "document_id": source.get("document_id"),
                "chunk_id": source.get("chunk_id"),
                "slide": source.get("slide"),
                "page": source.get("page"),
                "start_time": source.get("start_time"),
                "end_time": source.get("end_time"),
            })
    return list(merged.values())


def build_graph(chunks: List[Dict[str, Any]], lesson_id: str | None = None) -> Dict[str, Any]:
    canonical_chunks = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        text = str(chunk.get("text") or "").strip()
        if not text:
            continue
        canonical_chunks.append(chunk)

    concept_candidates = []
    for chunk in canonical_chunks:
        for concept in extract_concepts_from_chunk(chunk):
            concept_candidates.append(concept)

    deduped = deduplicate_concepts(concept_candidates)
    final_nodes = _merge_sources(deduped)
    final_edges = extract_relationships(final_nodes, canonical_chunks)
    graph = {
        "lesson_id": lesson_id or (canonical_chunks[0]["document_id"] if canonical_chunks else "lesson"),
        "nodes": final_nodes,
        "edges": final_edges,
    }
    return graph
