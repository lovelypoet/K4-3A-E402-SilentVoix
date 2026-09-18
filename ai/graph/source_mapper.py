from typing import Any, Dict, List


def map_source_to_concepts(graph: Dict[str, Any], current_slide: int | None = None, current_time: float | None = None) -> List[str]:
    active: List[str] = []
    for node in graph.get("nodes") or []:
        sources = node.get("sources") or []
        for source in sources:
            if current_slide is not None and source.get("slide") == current_slide:
                active.append(node["id"])
            if current_time is not None:
                start = source.get("start_time")
                end = source.get("end_time")
                if start is not None and end is not None and start <= current_time <= end:
                    active.append(node["id"])
    return sorted(set(active))
