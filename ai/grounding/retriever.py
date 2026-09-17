from typing import Any, Dict, List


class GroundingRetriever:
    def __init__(self, graph: Dict[str, Any]):
        self.graph = graph

    def find_concept(self, concept_id: str) -> Dict[str, Any] | None:
        for node in self.graph.get("nodes") or []:
            if node.get("id") == concept_id:
                return node
        return None

    def retrieve_evidence(self, concept_id: str) -> List[Dict[str, Any]]:
        node = self.find_concept(concept_id)
        if not node:
            return []
        return node.get("sources") or []

    def has_sufficient_evidence(self, concept_id: str) -> bool:
        evidence = self.retrieve_evidence(concept_id)
        return bool(evidence)
