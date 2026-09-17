from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.pipeline import build_graph, generate_quiz


SAMPLE_CHUNKS = [
    {
        "chunk_id": "chunk_017",
        "document_id": "lecture_04",
        "text": "Gradient descent is an optimization algorithm used to minimize a loss function.",
        "source": {"type": "slide", "page": 17, "slide": 17, "start_time": None, "end_time": None},
    },
    {
        "chunk_id": "chunk_018",
        "document_id": "lecture_04",
        "text": "The loss function measures prediction error and the gradient descent algorithm updates parameters by moving in the direction of steepest descent.",
        "source": {"type": "video", "page": None, "slide": None, "start_time": 742.0, "end_time": 813.0},
    },
    {
        "chunk_id": "chunk_019",
        "document_id": "lecture_04",
        "text": "Regression is a type of supervised learning used to predict continuous values.",
        "source": {"type": "slide", "page": 19, "slide": 19, "start_time": None, "end_time": None},
    },
]


def main() -> None:
    graph = build_graph(SAMPLE_CHUNKS, lesson_id="lecture_04")
    print("GRAPH")
    print(json.dumps(graph, indent=2, ensure_ascii=False))

    quiz = generate_quiz(graph, "gradient_descent", difficulty="medium")
    print("\nQUIZ")
    print(json.dumps(quiz, indent=2, ensure_ascii=False))

    unsupported = generate_quiz(graph, "adamw", difficulty="easy")
    print("\nUNSUPPORTED")
    print(json.dumps(unsupported, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
