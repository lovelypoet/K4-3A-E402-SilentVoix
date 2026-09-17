import re
from typing import Any, Dict, List

from ai.extraction.normalizer import canonical_concept_id, normalize_concept_label


CONCEPT_PATTERNS = {
    "gradient_descent": ["gradient descent", "gradient-descent", "gd"],
    "loss_function": ["loss function", "cost function"],
    "regression": ["regression"],
    "supervised_learning": ["supervised learning"],
    "classification": ["classification"],
    "clustering": ["clustering"],
    "decision_tree": ["decision tree"],
    "k_means": ["k-means", "k means"],
    "feature_vector": ["feature vector"],
    "weight_vector": ["weight vector"],
    "training_data": ["training data"],
    "testing_data": ["testing data"],
    "neural_network": ["neural network"],
    "layer": ["layer", "layers"],
    "neuron": ["neuron", "neurons"],
    "overfitting": ["overfitting"],
    "underfitting": ["underfitting"],
    "linear_regression": ["linear regression"],
    "linear_function": ["linear function"],
    "gradient_boosting": ["gradient boosting"],
    "embedding": ["embedding", "embeddings"],
    "vector": ["vector", "vectors"],
    "transformer": ["transformer"],
    "self_attention": ["self-attention", "self attention"],
    "softmax": ["softmax"],
    "adamw": ["adamw"],
}


def _match_concepts(text: str) -> List[Dict[str, Any]]:
    cleaned = text.strip()
    if not cleaned:
        return []

    found: List[Dict[str, Any]] = []
    text_lower = cleaned.lower()
    for concept_id, aliases in CONCEPT_PATTERNS.items():
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in text_lower:
                label = alias if alias_lower == alias_lower else alias
                found.append({
                    "id": concept_id,
                    "label": label.title() if concept_id == "gradient_descent" else alias.title(),
                    "description": _describe_concept(concept_id, cleaned),
                    "source": {},
                })
                break
    return found


def _describe_concept(concept_id: str, text: str) -> str:
    descriptions = {
        "gradient_descent": "An optimization algorithm used to minimize a loss function.",
        "loss_function": "A function that measures prediction error.",
        "regression": "A supervised learning task for predicting continuous values.",
        "supervised_learning": "A learning paradigm that uses labeled examples.",
        "classification": "A supervised learning task for predicting discrete classes.",
        "clustering": "A form of unsupervised learning that groups similar data points.",
        "decision_tree": "A tree-shaped model that makes decisions based on feature thresholds.",
        "k_means": "A clustering algorithm that partitions data into k groups.",
        "feature_vector": "A representation of an instance as a set of features.",
        "weight_vector": "A vector of model weights used in learning.",
        "training_data": "The data used to fit a model.",
        "testing_data": "The data used to evaluate a model.",
        "neural_network": "A model composed of connected layers and neurons.",
        "layer": "A set of neurons or processing units in a model.",
        "neuron": "A computational unit in a neural network.",
        "overfitting": "A condition where a model fits the training data too closely.",
        "underfitting": "A condition where a model is too simple to capture the pattern.",
        "linear_regression": "A regression model using a linear function.",
        "linear_function": "A function following a linear relationship between variables.",
        "gradient_boosting": "An ensemble method that builds trees sequentially to reduce error.",
        "embedding": "A dense vector representation of some input.",
        "vector": "An ordered list of numbers used to represent data.",
        "transformer": "A neural architecture that uses self-attention to model sequences.",
        "self_attention": "A mechanism that relates elements within a sequence.",
        "softmax": "A function used to convert scores to probabilities.",
        "adamw": "An optimizer that adapts learning rates while using weight decay.",
    }
    return descriptions.get(concept_id, text)


def extract_concepts_from_chunk(chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
    text = str(chunk.get("text") or "").strip()
    if not text:
        return []

    concepts = []
    for concept in _match_concepts(text):
        concept["source"] = {
            "document_id": chunk.get("document_id"),
            "chunk_id": chunk.get("chunk_id"),
            "slide": (chunk.get("source") or {}).get("slide"),
            "page": (chunk.get("source") or {}).get("page"),
            "start_time": (chunk.get("source") or {}).get("start_time"),
            "end_time": (chunk.get("source") or {}).get("end_time"),
        }
        concept["id"] = canonical_concept_id(concept.get("label", concept["id"]))
        concepts.append(concept)
    return concepts
