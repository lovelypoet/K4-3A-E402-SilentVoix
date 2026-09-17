import json
from typing import Any, Dict, List


def validate_graph(graph: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(graph, dict):
        raise ValueError("Graph must be a dictionary.")

    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    node_ids = [node["id"] for node in nodes if isinstance(node, dict)]

    duplicates = [value for value in set(node_ids) if node_ids.count(value) > 1]
    if duplicates:
        raise ValueError(f"Duplicate node IDs detected: {duplicates}")

    for edge in edges:
        if edge.get("source") not in node_ids:
            raise ValueError(f"Edge source missing: {edge}")
        if edge.get("target") not in node_ids:
            raise ValueError(f"Edge target missing: {edge}")

    try:
        json.dumps(graph)
    except Exception as exc:  # pragma: no cover
        raise ValueError("Graph is not JSON serializable") from exc

    return {"status": "valid", "node_count": len(nodes), "edge_count": len(edges)}
