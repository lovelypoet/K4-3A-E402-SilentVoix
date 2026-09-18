from evals.evaluators.quiz_evaluator import evaluate_quiz
from evals.metrics import classification_metrics, concept_metrics, relation_metrics


def test_concept_metrics_precision_recall_f1():
    result = concept_metrics(["a", "b"], ["a", "c"])
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5


def test_relation_metrics_are_set_based():
    result = relation_metrics(["a->b:type_of"], ["a->b:type_of", "b->a:type_of"])
    assert result["precision"] == 0.5
    assert result["recall"] == 1.0


def test_decision_confusion_matrix():
    result = classification_metrics(["GENERATE_QUIZ", "REFUSE_UNGROUNDED"], ["GENERATE_QUIZ", "GENERATE_QUIZ"], {"GENERATE_QUIZ", "DISAMBIGUATE", "REFUSE_UNGROUNDED"})
    assert result["accuracy"] == 0.5
    assert result["confusion_matrix"]["REFUSE_UNGROUNDED"]["GENERATE_QUIZ"] == 1


def test_quiz_critical_failure_overrides_score():
    graph = {"nodes": [{"id": "x", "sources": [{"chunk_id": "c1"}]}], "edges": []}
    quiz = {"decision": "GENERATE_QUIZ", "concept_id": "x", "question": "What is x?", "options": ["right", "wrong"], "correct_answer": "right", "explanation": "A grounded explanation.", "citations": []}
    result = evaluate_quiz(graph, quiz)
    assert result["critical_failure"] is True
    assert result["classification"] == "fail"


def test_quiz_refusal_has_no_fabricated_content():
    result = evaluate_quiz({"nodes": [], "edges": []}, {"decision": "REFUSE_UNGROUNDED", "concept_id": "missing", "question": "", "options": [], "correct_answer": "", "explanation": "Not supported.", "citations": []})
    assert result["critical_failure"] is False
    assert result["score"] == 20
