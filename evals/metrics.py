from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


def _prf(tp: int, predicted: int, expected: int) -> dict[str, float]:
    precision = tp / predicted if predicted else 0.0
    recall = tp / expected if expected else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def concept_metrics(expected: Iterable[str], predicted: Iterable[str]) -> dict[str, Any]:
    expected_set = set(expected)
    predicted_set = set(predicted)
    return {
        **_prf(len(expected_set & predicted_set), len(predicted_set), len(expected_set)),
        "true_positive": sorted(expected_set & predicted_set),
        "false_positive": sorted(predicted_set - expected_set),
        "false_negative": sorted(expected_set - predicted_set),
    }


def relation_metrics(expected: Iterable[str], predicted: Iterable[str]) -> dict[str, Any]:
    return concept_metrics(expected, predicted)


def classification_metrics(expected: Iterable[str], predicted: Iterable[str], labels: Iterable[str] | None = None) -> dict[str, Any]:
    expected_values = list(expected)
    predicted_values = list(predicted)
    label_set = set(labels or expected_values + predicted_values)
    per_class: dict[str, dict[str, float]] = {}
    matrix = {label: {other: 0 for other in sorted(label_set)} for label in sorted(label_set)}
    for actual, guess in zip(expected_values, predicted_values):
        matrix.setdefault(actual, {}).setdefault(guess, 0)
        matrix[actual][guess] += 1
    for label in sorted(label_set):
        tp = sum(1 for actual, guess in zip(expected_values, predicted_values) if actual == label and guess == label)
        predicted_count = sum(1 for guess in predicted_values if guess == label)
        expected_count = sum(1 for actual in expected_values if actual == label)
        per_class[label] = _prf(tp, predicted_count, expected_count)
    correct = sum(actual == guess for actual, guess in zip(expected_values, predicted_values))
    return {
        "accuracy": correct / len(expected_values) if expected_values else 0.0,
        "per_class": per_class,
        "confusion_matrix": matrix,
        "support": len(expected_values),
    }


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def median(values: Iterable[float]) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2


def score_distribution(values: Iterable[int]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))
