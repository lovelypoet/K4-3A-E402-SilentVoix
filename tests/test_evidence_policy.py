from ai.pipeline import build_graph, generate_quiz
from ai.quiz.decision import analyze_quiz_evidence, decide_quiz
from ai.quiz.validator import validate_quiz_output


def chunk(chunk_id, text):
    return {
        "chunk_id": chunk_id,
        "document_id": "doc",
        "text": text,
        "source": {"type": "slide", "slide": 1},
    }


def test_mention_only_source_refuses():
    graph = build_graph([chunk("mention", "The lecture mentions softmax.")])
    analysis = analyze_quiz_evidence(graph, "softmax")
    assert analysis["decision"] == "REFUSE_UNGROUNDED"
    assert decide_quiz(graph, "softmax") == "REFUSE_UNGROUNDED"


def test_competing_concepts_disambiguate():
    graph = build_graph([chunk("ambiguous", "The lecture mentions gradient descent and gradient boosting.")])
    assert decide_quiz(graph, "gradient_descent") == "DISAMBIGUATE"


def test_explanatory_source_can_generate():
    graph = build_graph([chunk("supported", "Regression predicts continuous values.")])
    assert decide_quiz(graph, "regression") == "GENERATE_QUIZ"


def test_relation_requires_explicit_evidence():
    graph = build_graph([chunk("cooccur", "Classification and clustering appear in the same overview.")])
    assert graph["edges"] == []


def test_feature_vector_is_not_plain_vector():
    graph = build_graph([chunk("phrase", "The lesson explains feature vectors.")])
    assert {node["id"] for node in graph["nodes"]} == {"feature_vector"}


def test_invalid_quiz_is_rejected_deterministically():
    graph = build_graph([chunk("supported", "Regression predicts continuous values.")])
    quiz = {
        "decision": "GENERATE_QUIZ",
        "concept_id": "regression",
        "question": "What is regression?",
        "options": ["It predicts continuous values.", "It predicts continuous values."],
        "correct_answer": "It predicts continuous values.",
        "explanation": "The source supports the answer.",
        "citations": [{"chunk_id": "supported"}],
    }
    result = validate_quiz_output(graph, quiz)
    assert result["valid"] is False
    assert "duplicate options" in result["failures"]
