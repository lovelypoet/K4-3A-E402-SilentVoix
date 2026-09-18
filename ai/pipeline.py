from __future__ import annotations

from typing import Any, Dict, List

from ai.extraction.concept_extractor import extract_concepts_from_chunk
from ai.extraction.normalizer import deduplicate_concepts
from ai.extraction.relationship_extractor import extract_relationships
from ai.graph.validator import validate_graph
from ai.quiz.generator import generate_quiz


def build_graph(chunks: List[Dict[str, Any]], lesson_id: str | None = None) -> Dict[str, Any]:
    valid_chunks: List[Dict[str, Any]] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        text = str(chunk.get("text") or "").strip()
        if not text:
            continue
        valid_chunks.append(chunk)

    concept_candidates = []
    for chunk in valid_chunks:
        concept_candidates.extend(extract_concepts_from_chunk(chunk))

    deduped = deduplicate_concepts(concept_candidates)
    graph_nodes = []
    for concept in deduped:
        graph_nodes.append({
            "id": concept["id"],
            "label": concept["label"],
            "description": concept["description"],
            "sources": []
        })

    merged_sources: Dict[str, List[Dict[str, Any]]] = {}
    for concept in concept_candidates:
        node_id = concept["id"]
        source = concept.get("source") or {}
        merged_sources.setdefault(node_id, [])
        if source not in merged_sources[node_id]:
            merged_sources[node_id].append({
                "document_id": source.get("document_id"),
                "chunk_id": source.get("chunk_id"),
                "slide": source.get("slide"),
                "page": source.get("page"),
                "start_time": source.get("start_time"),
                "end_time": source.get("end_time"),
                "text": source.get("text"),
            })

    for node in graph_nodes:
        node["sources"] = merged_sources.get(node["id"], [])

    graph = {
        "lesson_id": lesson_id or (valid_chunks[0].get("document_id") if valid_chunks else "lesson"),
        "nodes": graph_nodes,
        "edges": extract_relationships(graph_nodes, valid_chunks),
    }

    validate_graph(graph)
    return graph


__all__ = ["build_graph", "generate_quiz"]
