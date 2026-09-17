from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ConceptNode:
    id: str
    label: str
    description: str
    sources: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "sources": self.sources,
        }
