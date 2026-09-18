import json
import sys
import tempfile
import argparse
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from ai.pipeline import build_graph, generate_quiz
from adaptive_learning import api
from adaptive_learning.storage import StorageManager
from fastapi.testclient import TestClient
from main import app

def evaluate(case, client, use_ai=False):
    checks = {}
    def check(stage, passed, expected, actual, reason=""):
        checks[stage] = {
            'status': 'PASS' if passed else 'FAIL',
            'expected': expected,
            'actual': actual,
            'reason': reason
        }

    # Setup specific IDs for this case
    api.db_storage.data = {
        'lessons': {},
        'documents': {},
        'chunks': [],
        'concepts': {},
        'source_mappings': {},
        'prerequisites': {},
        'student_attempts': {}
    }
    
    lid = 'eval_' + case['id']
    student_id = 'student_' + case['id']
    source = case['expected_source'] or {'document_id': 'empty_document'}
    slide_number = source.get('slide')
    
    # 1. Upload & Ingest (Mocking extraction with actual DB insertion to simulate Upload completion)
    chunk = {
        'document_id': source['document_id'],
        'chunk_id': lid + '_chunk',
        'text': case['input_chunk'],
        'source': {'type': 'slide', **source}
    }
    api.db_storage.data.setdefault('lessons', {})[lid] = {'lesson_id': lid, 'title': f"Test {case['id']}"}
    api.db_storage.data.setdefault('chunks', []).append({'lesson_id': lid, 'slide': slide_number, 'text': case['input_chunk']})
    
    # Generate Graph
    graph = build_graph([chunk], lesson_id=lid) if use_ai else {
        'nodes': [{'id': c, 'label': c, 'sources': [source]} for c in case['expected_concepts']],
        'edges': [{'source': e.split('->')[0], 'target': e.split('->')[1].split(':')[0], 'relation': e.split(':')[1]} for e in case['expected_relationships']]
    }
    
    # Insert graph to DB to simulate real backend state
    for node in graph.get('nodes', []):
        api.db_storage.data.setdefault('concepts', {})[node['id']] = {'concept_id': node['id'], 'name': node.get('label', node['id']), 'lesson_id': lid}
        api.db_storage.data.setdefault('source_mappings', {})[node['id']] = {**source, 'lesson_id': lid}
    for edge in graph.get('edges', []):
        if edge['relation'] == 'prerequisite_of':
            api.db_storage.data.setdefault('prerequisites', {}).setdefault(edge['target'], []).append(edge['source'])
            
    # 2. Graph fetch (API)
    graph_response = client.get(f'/adaptive/knowledge-graph/{lid}')
    check('Graph API', graph_response.status_code == 200, 200, graph_response.status_code, "Fetch graph successfully")

    # 3. Video Sync (Slide mapping)
    if slide_number is not None:
        sync_resp = client.get(f'/adaptive/concepts/by-slide/{slide_number}', params={'lesson_id': lid})
        check('Video Sync', sync_resp.status_code == 200, 200, sync_resp.status_code, "Slide to concept mapping")

    # Determine concept to quiz
    cid = case.get('quiz_concept_id') or (case['expected_concepts'][0] if case['expected_concepts'] else 'unsupported_concept')
    
    # 4. Quiz
    if use_ai:
        quiz = generate_quiz(graph, cid, difficulty='medium')
    else:
        quiz = {'decision': case['expected_quiz_decision'], 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 'A'}
        
    check('Quiz Generation', quiz['decision'] == case['expected_quiz_decision'], case['expected_quiz_decision'], quiz['decision'], "Quiz decision match")
    
    if quiz['decision'] == 'GENERATE_QUIZ' and cid in api.db_storage.data.get('concepts', {}):
        # 5. Answer Wrong
        wrong_option = next((opt for opt in quiz['options'] if opt != quiz['correct_answer']), 'B')
        answer_resp = client.post('/adaptive/quiz/answer', params={'student_id': student_id}, json={
            'quiz_id': lid + '_q1',
            'concept_id': cid,
            'is_correct': False,
            'difficulty': 3
        })
        check('Answer API', answer_resp.status_code == 200, 200, answer_resp.status_code, "Submit wrong answer")
        
        # 6. Mastery Update & 7. Weak Concept
        mastery_resp = client.get(f'/adaptive/mastery/{student_id}')
        mastery_state = mastery_resp.json().get('mastery_summary', {}).get(cid, {}).get('state')
        check('Mastery Update', mastery_state == 'weak', 'weak', mastery_state, "Concept should be weak after wrong answer")
        
        # 8 & 9. Prerequisite & Recommendation
        rec_resp = client.get(f'/adaptive/recommendation/{student_id}', params={'current_concept_id': cid})
        if rec_resp.status_code == 200:
            rec_data = rec_resp.json()
            rec_source_slide = rec_data.get('source', {}).get('slide')
            
            # Expected prerequisite: if the case has relationships ending in prerequisite_of -> cid
            expected_prereqs = [e.split('->')[0] for e in case['expected_relationships'] if e.endswith('->'+cid+':prerequisite_of')]
            expected_rec_id = expected_prereqs[0] if expected_prereqs else cid
            
            # Convert actual recommended label back to concept ID if possible
            actual_rec_label = rec_data.get('recommended_concept')
            actual_rec_id = next((n['id'] for n in graph.get('nodes', []) if n.get('label', n['id']) == actual_rec_label), None)
            
            check('Recommendation', actual_rec_id == expected_rec_id, expected_rec_id, actual_rec_id, "Recommend correct weak prerequisite")
            
            # 10 & 11. Click -> Correct Video Timestamp
            if rec_source_slide is not None:
                dest_resp = client.get(f"/adaptive/lessons/{lid}/slides/{rec_source_slide}")
                check('UI Click Mock', dest_resp.status_code == 200 and dest_resp.json().get('found', False), True, dest_resp.status_code == 200 and dest_resp.json().get('found', False), "Clicking recommendation goes to valid slide/timestamp")
            else:
                check('UI Click Mock', False, "Has slide", "No slide in recommendation", "Missing source slide in recommendation")
        else:
            check('Recommendation', False, 200, rec_resp.status_code, "Recommendation API failed")
            check('UI Click Mock', False, "Success", "Failed", "Recommendation failed")

    return {'case_id': case['id'], 'checks': checks}

def run(full_ai=False):
    cases_path = ROOT / 'tests/golden/cases.json'
    cases = json.loads(cases_path.read_text(encoding='utf-8'))
    results = []

    with tempfile.TemporaryDirectory() as directory:
        storage = StorageManager(str(Path(directory) / 'db.json'))
        with patch.object(api, 'db_storage', storage), TestClient(app) as client:
            for case in cases:
                try:
                    result = evaluate(case, client, use_ai=full_ai)
                except Exception as exc:
                    result = {'case_id': case['id'], 'checks': {'Execution': {'status': 'ERROR', 'actual': str(exc), 'reason': 'Exception occurred'}}}
                results.append(result)

    # Compile metrics
    metrics = {}
    for res in results:
        for stage, value in res['checks'].items():
            counts = metrics.setdefault(stage, {'PASS': 0, 'FAIL': 0, 'ERROR': 0})
            counts[value['status']] += 1

    total_cases = len(cases)
    overall_pass = sum(1 for r in results if all(c['status'] == 'PASS' for c in r['checks'].values()))
    pass_rate = (overall_pass / total_cases) * 100 if total_cases > 0 else 0

    print("=" * 50)
    print("KẾT QUẢ ĐÁNH GIÁ E2E (E2E EVALUATION REPORT)")
    print("=" * 50)
    print(f"Tổng số cases đã test: {total_cases}")
    print(f"Hệ thống hiện tại hoạt động đúng {pass_rate:.1f}% trên golden set.")
    print("-" * 50)
    print("Chi tiết Metrics:")
    for m, c in metrics.items():
        print(f" - {m}: PASS={c['PASS']}, FAIL={c['FAIL']}, ERROR={c['ERROR']}")
    
    print("-" * 50)
    print("Chi tiết các cases FAIL:")
    fail_count = 0
    for res in results:
        failed_steps = {k: v for k, v in res['checks'].items() if v['status'] != 'PASS'}
        if failed_steps:
            fail_count += 1
            print(f"Case {res['case_id']} - FAIL ở các bước:")
            for step, details in failed_steps.items():
                print(f"  > {step}: Expected {details.get('expected')} | Actual {details.get('actual')} | Reason: {details.get('reason')}")

    if fail_count == 0:
        print("Tất cả cases đều PASS!")
        
    report = {
        "total_cases": total_cases,
        "pass_rate": pass_rate,
        "metrics": metrics,
        "results": results
    }
    
    report_path = ROOT / "eval/e2e_eval_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print("=" * 50)
    print(f"Đã lưu báo cáo chi tiết vào: {report_path}")

    return 1 if fail_count > 0 else 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run E2E Eval")
    parser.add_argument('--full-ai', action='store_true', help="Use real AI pipeline instead of mocked output")
    args = parser.parse_args()
    sys.exit(run(full_ai=args.full_ai))
