from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai.pipeline import build_graph, generate_quiz
from ai.quiz.decision import decide_quiz
from evals.evaluators.grounding_evaluator import evaluate_grounding
from evals.evaluators.quiz_evaluator import evaluate_quiz
from evals.metrics import classification_metrics, concept_metrics, mean, median, relation_metrics, score_distribution

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "datasets" / "cases.json"
REPORTS = ROOT / "reports"


def _relation_strings(graph: dict[str, Any]) -> list[str]:
    return [f"{edge.get('source')}->{edge.get('target')}:{edge.get('relation')}" for edge in graph.get("edges") or []]


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    graph = build_graph(case.get("chunks") or [])
    predicted_concepts = [node.get("id") for node in graph.get("nodes") or []]
    predicted_relations = _relation_strings(graph)
    requested = case.get("requested_concept") or ""
    quiz = generate_quiz(graph, requested, difficulty=case.get("difficulty", "medium"))
    concept_result = concept_metrics(case.get("expected_concepts") or [], predicted_concepts)
    relation_result = relation_metrics(case.get("expected_relationships") or [], predicted_relations)
    pre_generation_decision = decide_quiz(graph, requested)
    decision_result = {"expected": case.get("expected_decision"), "predicted": pre_generation_decision, "final_output": quiz.get("decision"), "correct": pre_generation_decision == case.get("expected_decision")}
    grounding_result = evaluate_grounding(graph, case.get("expected_source"), quiz.get("citations") or [])
    quiz_result = evaluate_quiz(graph, quiz, case)
    if quiz.get("decision") == "VALIDATION_FAILED" and case.get("expected_decision") == "GENERATE_QUIZ":
        quiz_result["critical_failure"] = True
        quiz_result["critical_reasons"].append("post-generation semantic validation withheld the quiz")
        quiz_result["classification"] = "fail"
    return {
        "case_id": case["case_id"], "category": case["category"], "synthetic": bool(case.get("synthetic")),
        "tags": case.get("tags") or [], "expected": case, "graph": graph, "quiz": quiz,
        "predicted_concepts": predicted_concepts, "predicted_relationships": predicted_relations,
        "concept_metrics": concept_result, "relation_metrics": relation_result,
        "decision": decision_result, "grounding": grounding_result, "quiz_evaluation": quiz_result,
    }


def _aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    concept = concept_metrics(
        [concept for result in results for concept in result["expected"].get("expected_concepts") or []],
        [concept for result in results for concept in result["predicted_concepts"]],
    )
    relation = relation_metrics(
        [relation for result in results for relation in result["expected"].get("expected_relationships") or []],
        [relation for result in results for relation in result["predicted_relationships"]],
    )
    expected_decisions = [result["decision"]["expected"] for result in results]
    predicted_decisions = [result["decision"]["predicted"] for result in results]
    decision = classification_metrics(expected_decisions, predicted_decisions, {"GENERATE_QUIZ", "DISAMBIGUATE", "REFUSE_UNGROUNDED"})
    quizzes = [result for result in results if result["quiz"].get("decision") == "GENERATE_QUIZ"]
    scores = [result["quiz_evaluation"]["score"] for result in quizzes]
    grounding = [result["grounding"] for result in results]
    false_generate = sum(result["decision"]["expected"] != "GENERATE_QUIZ" and result["decision"]["predicted"] == "GENERATE_QUIZ" for result in results)
    false_refuse = sum(result["decision"]["expected"] == "GENERATE_QUIZ" and result["decision"]["predicted"] != "GENERATE_QUIZ" for result in results)
    critical = [result["case_id"] for result in results if result["quiz_evaluation"]["critical_failure"]]
    final_quizzes = [result for result in results if result["quiz"].get("decision") == "GENERATE_QUIZ"]
    score_values = [result["quiz_evaluation"]["score"] for result in final_quizzes]
    classifications = {name: sum(result["quiz_evaluation"]["classification"] == name for result in final_quizzes) for name in ("strong", "acceptable", "needs_improvement", "fail")}
    return {
        "dataset_size": len(results), "synthetic_cases": sum(result["synthetic"] for result in results), "real_cases": sum(not result["synthetic"] for result in results),
        "concept": concept, "relationship": relation, "grounding": {
            "citation_accuracy": mean(item["citation_accuracy"] for item in grounding),
            "source_recall": mean(item["source_recall"] for item in grounding),
            "unsupported_claim_rate": mean(item["unsupported_claim"] for item in grounding),
        },
        "decision": {**decision, "false_generate": false_generate, "false_refuse": false_refuse},
        "quiz": {"generated_count": len(quizzes), "publishable_count": len(final_quizzes), "mean_score": mean(scores), "median_score": median(scores), "score_distribution": score_distribution(scores), "acceptable_or_better_rate": mean(result["quiz_evaluation"]["score"] >= 15 for result in quizzes), "semantic_mean": mean(score_values), "semantic_median": median(score_values), "classification_counts": classifications, "critical_failures": critical},
    }


def _error_categories(results: list[dict[str, Any]]) -> dict[str, int]:
    categories: dict[str, int] = {}
    def add(name: str) -> None:
        categories[name] = categories.get(name, 0) + 1
    for result in results:
        if result["concept_metrics"]["false_positive"]: add("CONCEPT: over-extraction or irrelevant concept")
        if result["concept_metrics"]["false_negative"]: add("CONCEPT: under-extraction")
        if result["relation_metrics"]["false_positive"]: add("RELATION: unsupported or wrong edge")
        if result["relation_metrics"]["false_negative"]: add("RELATION: missing edge or wrong direction/type")
        if result["grounding"]["unsupported_claim"]: add("GROUNDING: wrong or missing citation")
        if result["decision"]["expected"] != "GENERATE_QUIZ" and result["decision"]["predicted"] == "GENERATE_QUIZ": add("DECISION: false GENERATE")
        if result["decision"]["expected"] == "GENERATE_QUIZ" and result["decision"]["predicted"] != "GENERATE_QUIZ": add("DECISION: false REFUSE or DISAMBIGUATE")
        for reason in result["quiz_evaluation"]["critical_reasons"]:
            add("QUIZ: " + reason)
    return dict(sorted(categories.items(), key=lambda item: (-item[1], item[0])))


def _write_reports(results: list[dict[str, Any]], aggregate: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "raw_predictions.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    (REPORTS / "baseline.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    (REPORTS / "iteration_1.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    quiz_report = {"dataset_size": aggregate["dataset_size"], "quiz": aggregate["quiz"], "generated_cases": [result for result in results if result["quiz"].get("decision") == "GENERATE_QUIZ"]}
    (REPORTS / "quiz_baseline.json").write_text(json.dumps(quiz_report, indent=2, ensure_ascii=False), encoding="utf-8")
    errors = _error_categories(results)
    (REPORTS / "error_analysis.md").write_text(f"# Error Analysis\n\nAll {aggregate['dataset_size']} cases are synthetic hand-curated fixtures; these results are not production validation.\n\n## Failure categories\n\n" + "\n".join(f"- **{name}**: {count}" for name, count in errors.items()) + "\n\n## Interpretation\n\nFailures should be triaged in this order: data/source metadata, deterministic validators, grounding/retrieval, prompt constraints, then model capability. This baseline does not justify fine-tuning by itself.\n", encoding="utf-8")
    (REPORTS / "fine_tuning_decision.md").write_text(f"# Fine-tuning Decision\n\n**Recommendation: MORE REAL DATA REQUIRED BEFORE DECISION.**\n\nThis baseline uses {aggregate['dataset_size']} synthetic cases and contains zero human-rated quizzes. Synthetic results are useful for contract and regression checks, but cannot establish production quality or justify fine-tuning. First collect real, source-annotated concept, relation, grounding, refusal, and human quiz-review examples. Fix deterministic schema/citation failures and source selection issues before comparing prompt, few-shot, validator, retrieval, and model changes.\n\nThe next experiment is a fixed real-data baseline with lecturer labels and the same report schema. Fine-tuning should only be reconsidered after repeated residual errors remain in one identified module after those simpler interventions.\n", encoding="utf-8")
    lines = ["# AI Evaluation Baseline", "", "This is an AS-IS baseline. The dataset is synthetic and must not be presented as real-world validation.", "", f"- Dataset: {aggregate['dataset_size']} cases ({aggregate['synthetic_cases']} synthetic, {aggregate['real_cases']} real)", f"- Concept F1: {aggregate['concept']['f1']:.3f}", f"- Relationship F1: {aggregate['relationship']['f1']:.3f}", f"- Citation accuracy: {aggregate['grounding']['citation_accuracy']:.3f}", f"- Unsupported claim rate: {aggregate['grounding']['unsupported_claim_rate']:.3f}", f"- Quiz decision accuracy: {aggregate['decision']['accuracy']:.3f}", f"- False GENERATE: {aggregate['decision']['false_generate']}", f"- False REFUSE: {aggregate['decision']['false_refuse']}", f"- Quiz mean score: {aggregate['quiz']['mean_score']:.2f}/20", f"- Quiz acceptable-or-better rate: {aggregate['quiz']['acceptable_or_better_rate']:.3f}", f"- Critical quiz failures: {len(aggregate['quiz']['critical_failures'])}", "", "## Quality bar", "", "The proposed MVP bar is at least 80% expected behavior, citation accuracy at least 90%, and zero critical unsupported-grounded generation. Synthetic-only results are **INCONCLUSIVE** for production quality.", "", "## Decision", "", "Fine-tuning decision: MORE REAL DATA REQUIRED BEFORE DECISION.", "", "Use `evals.reports/raw_predictions.json` for per-case predictions and `python -m evals.run_eval --category quiz` for a filtered run."]
    (REPORTS / "baseline.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    comparison = """# Baseline vs Iteration 1

Ground-truth corrections mean some deltas are not attributable to pipeline behavior alone. Iteration 1 also adds evidence policy and deterministic validation; synthetic results remain non-production evidence.

| Metric | Original Baseline | Iteration 1 | Delta |
|---|---:|---:|---:|
| Concept F1 | 1.000 | %.3f | %+.3f |
| Relation F1 | 0.909 | %.3f | %+.3f |
| Citation Accuracy | 0.885 | %.3f | %+.3f |
| Source Recall | 0.923 | %.3f | %+.3f |
| Unsupported Claim Rate | 0.115 | %.3f | %+.3f |
| Decision Accuracy | 0.885 | %.3f | %+.3f |
| False GENERATE | 3 | %d | %+.0f |
| False REFUSE | 0 | %d | %+.0f |
| Critical Quiz Failures | 3 | %d | %+.0f |

The quality bar remains frozen: at least 80%% expected behavior, citation accuracy at least 90%%, and zero unsupported-grounded critical failures.
""" % (aggregate["concept"]["f1"], aggregate["concept"]["f1"] - 1.0, aggregate["relationship"]["f1"], aggregate["relationship"]["f1"] - 0.909, aggregate["grounding"]["citation_accuracy"], aggregate["grounding"]["citation_accuracy"] - 0.885, aggregate["grounding"]["source_recall"], aggregate["grounding"]["source_recall"] - 0.923, aggregate["grounding"]["unsupported_claim_rate"], aggregate["grounding"]["unsupported_claim_rate"] - 0.115, aggregate["decision"]["accuracy"], aggregate["decision"]["accuracy"] - 0.885, aggregate["decision"]["false_generate"], aggregate["decision"]["false_generate"] - 3, aggregate["decision"]["false_refuse"], aggregate["decision"]["false_refuse"], len(aggregate["quiz"]["critical_failures"]), len(aggregate["quiz"]["critical_failures"]) - 3)
    (REPORTS / "iteration_1.md").write_text(f"# Iteration 1\n\nCorrected synthetic set: {aggregate['dataset_size']} cases, all synthetic.\n\n- Concept F1: {aggregate['concept']['f1']:.3f}\n- Relation F1: {aggregate['relationship']['f1']:.3f}\n- Citation accuracy: {aggregate['grounding']['citation_accuracy']:.3f}\n- Unsupported claim rate: {aggregate['grounding']['unsupported_claim_rate']:.3f}\n- Decision accuracy: {aggregate['decision']['accuracy']:.3f}\n- False GENERATE: {aggregate['decision']['false_generate']}\n- False REFUSE: {aggregate['decision']['false_refuse']}\n- Publishable quizzes: {aggregate['quiz']['publishable_count']}\n- Semantic critical failures: {len(aggregate['quiz']['critical_failures'])}\n\nResult: INCONCLUSIVE for production because no human-labeled real cases are available.\n", encoding="utf-8")
    (REPORTS / "baseline_vs_iteration_1.md").write_text(comparison, encoding="utf-8")
    (REPORTS / "real_baseline.json").write_text(json.dumps({"status": "UNAVAILABLE", "lessons": 0, "cases": 0, "quiz_cases": 0, "human_reviewers": 0, "reason": "No human-labeled real gold cases are available."}, indent=2), encoding="utf-8")
    (REPORTS / "real_baseline.md").write_text("# REAL HUMAN-LABELED EVALUATION\n\nStatus: UNAVAILABLE. No human-labeled real gold cases are available. See `evals/real/lesson_manifest.json` for corpus exclusions and `evals/real/README.md` for the annotation plan.\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic AI quality evaluation without changing model behavior.")
    parser.add_argument("--category", choices=["concept", "relation", "grounding", "refusal", "quiz"], default=None)
    parser.add_argument("--case-id", default=None)
    args = parser.parse_args()
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    selected = [case for case in cases if (not args.category or case["category"] == args.category) and (not args.case_id or case["case_id"] == args.case_id)]
    if not selected:
        parser.error("No evaluation cases matched the requested filter")
    results = [evaluate_case(case) for case in selected]
    aggregate = _aggregate(results)
    _write_reports(results, aggregate)
    print("AI EVALUATION SUMMARY")
    print(f"Cases: {aggregate['dataset_size']} ({aggregate['synthetic_cases']} synthetic, {aggregate['real_cases']} real)")
    print(f"Concept F1: {aggregate['concept']['f1']:.3f}")
    print(f"Relationship F1: {aggregate['relationship']['f1']:.3f}")
    print(f"Citation Accuracy: {aggregate['grounding']['citation_accuracy']:.3f}")
    print(f"Unsupported Claim Rate: {aggregate['grounding']['unsupported_claim_rate']:.3f}")
    print(f"Quiz Decision Accuracy: {aggregate['decision']['accuracy']:.3f} (false GENERATE={aggregate['decision']['false_generate']}, false REFUSE={aggregate['decision']['false_refuse']})")
    print(f"Quiz Mean Score: {aggregate['quiz']['mean_score']:.2f}/20; critical failures={len(aggregate['quiz']['critical_failures'])}")
    print("RESULT: INCONCLUSIVE (synthetic evaluation only)")
    print("FINE-TUNING DECISION: MORE REAL DATA REQUIRED BEFORE DECISION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
