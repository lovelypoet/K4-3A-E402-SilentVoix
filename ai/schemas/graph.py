from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "evidence": self.evidence,
        }


@dataclass
class KnowledgeGraph:
    lesson_id: str
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "nodes": self.nodes,
            "edges": [edge.to_dict() for edge in self.edges],
        }
