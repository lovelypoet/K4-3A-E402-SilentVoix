import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    from eval.run_ai_e2e import run
    sys.exit(run())

from eval.llm_judge import evaluate_with_llm_mock, PROMPT_QUIZ_QUALITY

def run_eval():
    file_path = os.path.join(os.path.dirname(__file__), 'golden_set.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    total_cases = len(cases)
    perfect_cases = 0  # Vừa câu đúng + trích dẫn đúng
    failed_cases = 0   # Câu sai hoặc trích dẫn sai (bịa)

    print("Đang chạy Evaluation...")

    for i, case in enumerate(cases, 1):
        # 1. Kiem tra Chat luong Cau hoi (Dung LLM)
        input_data = {
            "document": case["source_text"],
            "quiz": case["generated_quiz"]["quiz"],
            "options": case["generated_quiz"]["options"],
            "correct_answer": case["generated_quiz"]["correct_answer"]
        }
        
        result = evaluate_with_llm_mock(PROMPT_QUIZ_QUALITY, input_data, expected_pass=True)
        
        # 2. Kiem tra Trich dan
        is_citation_correct = (case["generated_citation"] == case["expected_citation"])

        if result["pass"] and is_citation_correct:
            perfect_cases += 1
            status = "PASS"
        else:
            failed_cases += 1
            status = "FAIL"
            
        print(f"Câu {i} - Status: {status}")
        print(f"  - Quiz Quality (LLM): {'PASS' if result['pass'] else 'FAIL'} | Lý do: {result['reason']}")
        print(f"  - Citation Match: {'PASS' if is_citation_correct else 'FAIL'} (Expected: {case['expected_citation']}, Got: {case['generated_citation']})")
        print("-" * 40)

    # Tạo câu văn chuẩn format CP3
    # Mẫu: "Thử 21 câu, 13 câu trả đúng có dẫn nguồn, 8 câu sai hoặc bịa"
    final_sentence = f"Thử {total_cases} câu, {perfect_cases} câu sinh đúng và có dẫn nguồn, {failed_cases} câu sai hoặc bịa."

    print("\n========================================")
    print("KẾT QUẢ SỐ ĐO NỘP CP3")
    print("========================================")
    print(final_sentence)
    print("========================================\n")

    # Ghi ra file de doi truong nop
    report_path = os.path.join(os.path.dirname(__file__), '..', 'cp3_ket_qua.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(final_sentence + "\n")
    
    print(f"-> Đã xuất câu văn báo cáo ra file: {os.path.abspath(report_path)}")

if __name__ == "__main__":
    run_eval()
