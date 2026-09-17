from typing import Any, Dict, List


class GroundingVerifier:
    def __init__(self, graph: Dict[str, Any]):
        self.graph = graph

    def verify_concept(self, concept_id: str) -> Dict[str, Any]:
        node = next((n for n in self.graph.get("nodes") or [] if n.get("id") == concept_id), None)
        if node is None:
            return {"status": "missing", "reason": "Concept is not present in the graph."}
        sources = node.get("sources") or []
        if not sources:
            return {"status": "missing_evidence", "reason": "Concept exists, but has no grounded source metadata."}
        return {"status": "grounded", "sources": sources}

    def verify_quiz_claim(self, concept_id: str, citations: List[Dict[str, Any]]) -> bool:
        source_ids = {source.get("chunk_id") for source in (self.graph.get("nodes") or []) if isinstance(source, dict)}
        if not citations:
            return False
        valid = True
        for citation in citations:
            chunk_id = citation.get("chunk_id")
            if chunk_id is None:
                valid = False
                continue
            if not any(
                source.get("chunk_id") == chunk_id for node in self.graph.get("nodes") or [] for source in (node.get("sources") or [])
            ):
                valid = False
        return valid
