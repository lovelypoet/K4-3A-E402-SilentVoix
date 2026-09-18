"""Offline API smoke evaluation; never treats fixture quizzes as generated output."""
import io
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    cases = json.loads((ROOT / "eval/golden_set.json").read_text(encoding="utf-8"))
    if cases and "input_file" in cases[0]:
        from eval.run_slide_eval import run as run_slide
        sys.exit(run_slide())

from docx import Document
from fastapi.testclient import TestClient
from adaptive_learning import api
from adaptive_learning.storage import StorageManager
from main import app


def run():
    cases = json.loads((ROOT / "eval/golden_set.json").read_text(encoding="utf-8"))
    results = []
    original_db, original_upload = api.db_storage, api.UPLOAD_DIR
    with tempfile.TemporaryDirectory() as directory:
        api.db_storage = StorageManager(str(Path(directory) / "storage.json"))
        api.UPLOAD_DIR = directory
        try:
            with TestClient(app) as client:
                for case in cases:
                    checks = {}
                    def check(name, passed, expected, actual):
                        checks[name] = {"status": "PASS" if passed else "FAIL",
                                        "expected": expected, "actual": actual}
                    try:
                        document = Document()
                        document.add_paragraph(case["source_text"])
                        stream = io.BytesIO()
                        document.save(stream)
                        response = client.post("/adaptive/upload", files={
                            "file": ("case.docx", stream.getvalue(),
                                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
                        check("upload", response.status_code == 200, 200, response.status_code)
                        response.raise_for_status()
                        lid = response.json()["lesson"]["lesson_id"]
                        detail = client.get(f"/adaptive/lessons/{lid}").json()
                        check("text_preservation", any(case["source_text"] in s["text"] for s in detail["slides"]),
                              case["source_text"], detail["slides"])
                        graph = client.get(f"/adaptive/knowledge-graph/{lid}").json()
                        nodes = graph["nodes"]
                        check("graph_available", bool(nodes), "at least one node", nodes)
                        cid = nodes[0]["id"]
                        slide = nodes[0]["slide"]
                        mapped = client.get(f"/adaptive/concepts/by-slide/{slide}", params={"lesson_id": lid}).json()
                        check("slide_mapping", cid in [c["concept_id"] for c in mapped["concepts"]], cid, mapped)
                        learner = f"eval_{case['id']}"
                        values = []
                        for correct, weight in [(True, 1), (False, 3)]:
                            answer = client.post("/adaptive/quiz/answer", params={"student_id": learner}, json={
                                "quiz_id": "fixture_attempt", "concept_id": cid,
                                "is_correct": correct, "difficulty": weight})
                            answer.raise_for_status()
                            values.append(answer.json()["new_mastery"])
                        check("weighted_mastery", values == [1.0, 0.25], [1.0, 0.25], values)
                        recommendation = client.get(f"/adaptive/recommendation/{learner}",
                                                    params={"current_concept_id": cid}).json()
                        check("leaf_recommendation_source", recommendation["recommended_concept"] == nodes[0]["label"]
                              and recommendation["source"].get("slide") == slide,
                              {"concept": nodes[0]["label"], "slide": slide}, recommendation)
                    except Exception as exc:
                        checks["execution"] = {"status": "ERROR", "actual": str(exc)}
                    for metric in ["concept_extraction_correctness", "relationship_correctness",
                                   "groundedness", "refusal_correctness", "video_sync",
                                   "prerequisite_recommendation", "browser_click_timestamp"]:
                        checks[metric] = {"status": "SKIP", "reason": "Missing expected annotations or pipeline/UI capability"}
                    check("fixture_citation_match", case["generated_citation"] == case["expected_citation"],
                          case["expected_citation"], case["generated_citation"])
                    results.append({"case_id": case["id"], "e2e_status": "INCOMPLETE", "checks": checks})
        finally:
            api.db_storage, api.UPLOAD_DIR = original_db, original_upload
    metrics = {}
    for result in results:
        for name, value in result["checks"].items():
            counts = metrics.setdefault(name, {s: 0 for s in ["PASS", "FAIL", "SKIP", "ERROR"]})
            counts[value["status"]] += 1
    report = {"mode": "offline_api_smoke", "total_cases": len(cases),
              "e2e_pass_rate": None, "e2e_incomplete": len(cases),
              "limitations": "DOCX wraps source_text on page 1; answers are supplied fixtures; no AI generation or browser execution.",
              "metrics": metrics, "cases": results}
    path = ROOT / "eval/backend_eval_results.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"total_cases": len(cases), "metrics": metrics, "e2e_pass_rate": None}, indent=2))
    print(f"Report: {path}")
    return 1 if any(c["status"] in {"FAIL", "ERROR"} for r in results for n, c in r["checks"].items()
                    if n != "fixture_citation_match") else 0


if __name__ == "__main__":
    sys.exit(run())
