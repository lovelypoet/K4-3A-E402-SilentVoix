import re
from typing import Dict, Iterable, List


VALID_RELATIONS = {"prerequisite_of", "part_of", "type_of", "used_for", "related_to"}


def normalize_concept_label(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    return text


def canonical_concept_id(label: str) -> str:
    label = normalize_concept_label(label)
    return label.replace(" ", "_")


def normalize_concept_aliases(raw_aliases: Iterable[str]) -> List[str]:
    normalized = set()
    for value in raw_aliases:
        if not value or not str(value).strip():
            continue
        normalized.add(canonical_concept_id(str(value)))
    return sorted(normalized)


def validate_relationship(relation: str) -> bool:
    return relation in VALID_RELATIONS


def concept_lookup_key(text: str) -> str:
    return canonical_concept_id(text)


def deduplicate_concepts(concepts: List[Dict]) -> List[Dict]:
    mapping: Dict[str, Dict] = {}
    for concept in concepts:
        key = concept.get("id") or concept_lookup_key(concept.get("label", ""))
        if key not in mapping:
            mapping[key] = {
                "id": key,
                "label": concept.get("label", "").strip(),
                "description": concept.get("description", "").strip(),
                "sources": [],
            }
        source = concept.get("source", {})
        if source:
            record = dict(source)
            if record not in mapping[key]["sources"]:
                mapping[key]["sources"].append(record)
        if concept.get("description") and not mapping[key]["description"]:
            mapping[key]["description"] = concept["description"].strip()
    return list(mapping.values())
