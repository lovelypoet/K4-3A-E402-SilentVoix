from typing import Any, Dict, List

from ai.extraction.normalizer import VALID_RELATIONS, validate_relationship


RELATION_MAP = {
    "loss_function": {"gradient_descent": "prerequisite_of"},
    "regression": {"supervised_learning": "type_of"},
    "decision_tree": {"supervised_learning": "type_of"},
    "k_means": {"clustering": "type_of"},
    "linear_regression": {"linear_function": "used_for"},
    "self_attention": {"transformer": "part_of"},
    "layer": {"neural_network": "part_of"},
    "gradient_descent": {"loss_function": "used_for"},
}


def extract_relationships(nodes: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    edges: List[Dict[str, Any]] = []
    node_ids = {node["id"] for node in nodes}

    for source_node in nodes:
        for target_node in nodes:
            if source_node["id"] == target_node["id"]:
                continue
            relation = RELATION_MAP.get(source_node["id"], {}).get(target_node["id"])
            if relation and validate_relationship(relation):
                evidence = []
                for chunk in chunks:
                    chunk_text = (chunk.get("text") or "").lower()
                    if source_node["label"].lower() in chunk_text and target_node["label"].lower() in chunk_text:
                        evidence.append(chunk.get("chunk_id"))
                if not evidence:
                    evidence = [chunk.get("chunk_id") for chunk in chunks if chunk.get("chunk_id")]
                edges.append({
                    "source": source_node["id"],
                    "target": target_node["id"],
                    "relation": relation,
                    "evidence": evidence[:3],
                })
    return edges
