"""Sequentially warm a small demo quiz cache.

Usage:
  python -m ai.quiz.pregenerate --request lesson_05 neural_network easy
  python -m ai.quiz.pregenerate  # uses the small default PDF/video demo set
"""

from __future__ import annotations

import argparse
import json
import time

from ai.quiz.api import QuizGenerateRequest, generate_quiz


DEFAULT_REQUESTS = [
    ("lesson_05", "neural_network", "easy"),
    ("lesson_05", "neural_network", "medium"),
    ("lesson_59", "neural_network", "easy"),
    ("lesson_59", "neural_network", "medium"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Sequentially pre-generate a small grounded quiz demo cache")
    parser.add_argument("--request", nargs=3, action="append", metavar=("LESSON_ID", "CONCEPT_ID", "DIFFICULTY"), help="Request one quiz")
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    args = parser.parse_args()
    requests = args.request or DEFAULT_REQUESTS
    for index, (lesson_id, concept_id, difficulty) in enumerate(requests):
        result = generate_quiz(QuizGenerateRequest(lesson_id=lesson_id, concept_id=concept_id, difficulty=difficulty))
        print(json.dumps({
            "lesson_id": lesson_id, "concept_id": concept_id, "difficulty": difficulty,
            "decision": result.get("decision"), "generator_type": result.get("generator_type"),
            "metadata": result.get("metadata"), "validation": result.get("validation"),
        }, ensure_ascii=False))
        if index < len(requests) - 1 and args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)


if __name__ == "__main__":
    main()

