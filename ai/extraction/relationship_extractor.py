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
}

RELATION_EVIDENCE = {
    "used_for": (" is used for ", " used for ", " is used to "),
    "prerequisite_of": (" prerequisite for ", " is a prerequisite for ", " prerequisite to ", " used to "),
    "type_of": (" is a type of ", " is an ", " is a ", " is supervised learning"),
    "part_of": (" is made of ", " consists of ", " part of ", " with self-attention"),
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
                        evidence_phrases = RELATION_EVIDENCE.get(relation, ())
                        if relation != "related_to" and not any(phrase in chunk_text for phrase in evidence_phrases):
                            continue
                        evidence.append(chunk.get("chunk_id"))
                if not evidence:
                    continue
                edges.append({
                    "source": source_node["id"],
                    "target": target_node["id"],
                    "relation": relation,
                    "evidence": evidence[:3],
                })
    return edges
