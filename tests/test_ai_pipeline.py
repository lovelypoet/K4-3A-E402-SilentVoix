import json

import pytest

from ai.pipeline import build_graph, generate_quiz


@pytest.fixture
def sample_chunks():
    return [
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


def test_concept_extraction_and_source_metadata(sample_chunks):
    graph = build_graph(sample_chunks)
    ids = {node["id"] for node in graph["nodes"]}
    assert "gradient_descent" in ids
    assert "loss_function" in ids
    assert "regression" in ids

    gradient = next(node for node in graph["nodes"] if node["id"] == "gradient_descent")
    assert gradient["sources"]
    assert any(source.get("chunk_id") == "chunk_017" for source in gradient["sources"])


def test_empty_chunk_does_not_crash():
    graph = build_graph([{"chunk_id": "empty", "document_id": "doc", "text": "   ", "source": {"type": "slide", "page": 1, "slide": 1}}])
    assert graph["nodes"] == []
    assert graph["edges"] == []


def test_deduplication_for_aliases():
    chunks = [
        {
            "chunk_id": "a",
            "document_id": "doc1",
            "text": "Gradient Descent is used for optimization.",
            "source": {"type": "slide", "page": 1, "slide": 1},
        },
        {
            "chunk_id": "b",
            "document_id": "doc1",
            "text": "The gradient descent algorithm minimizes error.",
            "source": {"type": "slide", "page": 2, "slide": 2},
        },
    ]
    graph = build_graph(chunks)
    gradient_nodes = [node for node in graph["nodes"] if node["id"] == "gradient_descent"]
    assert len(gradient_nodes) == 1
    assert len(gradient_nodes[0]["sources"]) >= 2


def test_relationships_are_valid_and_supported(sample_chunks):
    graph = build_graph(sample_chunks)
    edge = next((e for e in graph["edges"] if e["source"] == "loss_function" and e["target"] == "gradient_descent"), None)
    assert edge is not None
    assert edge["relation"] in {"prerequisite_of", "used_for", "related_to"}
    assert edge["evidence"]

    for relation in graph["edges"]:
        assert relation["source"] in {node["id"] for node in graph["nodes"]}
        assert relation["target"] in {node["id"] for node in graph["nodes"]}


def test_graph_integrity_and_json_serialization(sample_chunks):
    graph = build_graph(sample_chunks)
    node_ids = [node["id"] for node in graph["nodes"]]
    assert len(node_ids) == len(set(node_ids))
    assert all(edge["source"] in node_ids for edge in graph["edges"])
    assert all(edge["target"] in node_ids for edge in graph["edges"])

    json.dumps(graph)
    assert graph["lesson_id"] == "lecture_04"
    assert all("sources" in node for node in graph["nodes"])


def test_grounding_and_citations(sample_chunks):
    graph = build_graph(sample_chunks)
    concept = next(node for node in graph["nodes"] if node["id"] == "gradient_descent")
    assert concept["sources"]
    assert any(source.get("slide") == 17 for source in concept["sources"])
    assert any(source.get("start_time") == 742.0 for source in concept["sources"])


def test_generate_quiz_known_concept(sample_chunks):
    graph = build_graph(sample_chunks)
    quiz = generate_quiz(graph, "gradient_descent", difficulty="medium")
    assert quiz["decision"] == "GENERATE_QUIZ"
    assert quiz["concept_id"] == "gradient_descent"
    assert quiz["correct_answer"] in quiz["options"]
    assert quiz["citations"]


def test_generate_quiz_disambiguate_for_insufficient_evidence():
    graph = {
        "lesson_id": "doc",
        "nodes": [
            {"id": "unknown_term", "label": "Unknown Term", "description": "", "sources": []},
            {"id": "unknown_term_2", "label": "Unknown Term 2", "description": "", "sources": []},
        ],
        "edges": [],
    }
    quiz = generate_quiz(graph, "unknown_term", difficulty="easy")
    assert quiz["decision"] in {"DISAMBIGUATE", "REFUSE_UNGROUNDED"}


def test_refuse_unsupported_concept(sample_chunks):
    graph = build_graph(sample_chunks)
    quiz = generate_quiz(graph, "adamw", difficulty="easy")
    assert quiz["decision"] == "REFUSE_UNGROUNDED"
    assert "not present" in quiz["explanation"].lower() or "unsupported" in quiz["explanation"].lower()


def test_hallucination_guard_for_adversarial_request(sample_chunks):
    graph = build_graph(sample_chunks)
    quiz = generate_quiz(graph, "adamw", difficulty="hard")
    assert quiz["decision"] == "REFUSE_UNGROUNDED"
    assert not quiz.get("question") or quiz["question"] == ""


def test_goldens_are_present():
    with open("tests/golden/cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)
    assert len(cases) >= 20
    assert any(case.get("expected_quiz_decision") == "GENERATE_QUIZ" for case in cases)
    assert any(case.get("expected_quiz_decision") == "REFUSE_UNGROUNDED" for case in cases)
