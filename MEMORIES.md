# TRẠNG THÁI DỰ ÁN
## 📌 Mục tiêu chính:
- [x] Xây dựng MVP AI/Knowledge Graph grounded
- [x] Tạo môi trường `.venv` và dependency backend + AI
- [x] Thêm schema, extraction, graph, grounding, quiz
- [x] Thêm tests và golden set
- [x] Chạy pytest và demo end-to-end
- [x] Merge backend branch vào `main`
## 🧠 Bối cảnh cốt lõi:
- Python 3.12.10; package chính ở `ai/`; entry point `ai.pipeline`
- Input là structured chunks có `document_id`, `chunk_id`, `text`, `source`
- Graph JSON gồm `lesson_id`, `nodes`, `edges`; quiz có grounding decisions
- Repo không có dataset `data/vlearn-pack/` hoặc backend/frontend Python sẵn có
## 🛠️ Tiến độ hiện tại:
- Đã tạo `.venv`; merge `origin/tai-backend` bằng commit `a0e07ca`
- Đã hợp nhất `requirements.txt`, `.gitignore`, `.env.example`; không giữ placeholder secret
- Đã thêm `ai/`, `tests/`, `tests/golden/cases.json`, `scripts/run_ai_demo.py`
- Đã thêm `ingest_slides_data()` và bỏ import test stale `upload_file_or_link`
- `pytest`: 13 passed; AI demo graph/quiz/refusal chạy thành công
- Còn 51 warning deprecation từ Starlette/Pydantic/httpx; không làm fail test
- Protective stash `pre-backend-merge-local-ai-state` vẫn được giữ
- Đã commit `15a9418`, merge remote index commit thành `80add66`, push thành công `origin/main`
- Đã cập nhật `spec.md`, commit `456fa24`, push thành công; `main` sạch và đồng bộ remote
## ➡️ Bước tiếp theo:
1. Khi có dữ liệu thật, bổ sung ingestion/evaluation thực tế; sau đó xử lý warning Pydantic/Starlette.

## 📊 AI evaluation baseline — 2026-09-18
- Đã thêm framework đánh giá riêng dưới `evals/`, không thay đổi prompt/model behavior và không thay thế software tests.
- Bộ dữ liệu baseline gồm 26 case hand-curated synthetic; 0 case real. Kết quả synthetic không được xem là production validation.
- Software baseline trước thay đổi: `pytest` 13 passed, 51 warnings. Evaluation metric tests sau thay đổi: 5 passed.
- AI baseline: Concept Precision/Recall/F1 = 1.000/1.000/1.000; Relationship Precision/Recall/F1 = 0.833/1.000/0.909.
- Grounding: citation accuracy = 0.885; source recall = 0.885; unsupported claim rate = 0.115.
- Quiz decision: accuracy = 0.885; false `GENERATE_QUIZ` = 3; false `REFUSE` = 0; decision failures tập trung ở các case cần `DISAMBIGUATE` hoặc refusal vì source yếu/không đủ.
- Quiz rubric là proposed MVP rubric 10 chiều, 0–2 điểm mỗi chiều, tối đa 20; 3 critical quiz failures được ghi nhận do generated quiz khi expected decision là disambiguation/refusal.
- Component mạnh nhất trong bộ synthetic là concept extraction; bottleneck hiện tại là relationship precision và grounding/decision safety.
- Fine-tuning chưa justified: cần real source-annotated cases và human quiz reviews trước; ưu tiên validator, source selection/grounding và decision threshold rồi mới đánh giá prompt/few-shot/model.
- Reports và raw predictions: `evals/reports/baseline.json`, `baseline.md`, `raw_predictions.json`, `quiz_baseline.json`, `error_analysis.md`, `fine_tuning_decision.md`.
- Next experiment: thêm dữ liệu lesson thật có nhãn concept/relation/source/refusal và lecturer review theo template tại `evals/human_review/`.

## 🔎 AI root-cause diagnosis — 2026-09-18
- Đã rerun baseline trước diagnosis: 18 software tests passed, 51 warnings; 26 synthetic evaluation cases; metrics giữ nguyên: Concept F1 1.000, Relation F1 0.909, citation accuracy 0.885, unsupported claim rate 0.115, decision accuracy 0.885.
- Có 10 unique failing cases: 4 case cùng extra edge `gradient_descent->loss_function:used_for`; 3 false `GENERATE_QUIZ`; 2 citation/gold-contract mismatch; 1 concept over-extraction (`vector` từ `feature_vector`).
- Root cause chính: `DECISION_POLICY` 3, `VALIDATOR` 2, `GROUND_TRUTH_ERROR` 5; `DATA`, `SOURCE_METADATA`, `SOURCE_MAPPING`, `RETRIEVAL`, `PROMPT`, `MODEL_CAPABILITY` = 0 primary cases.
- 100% (10/10) failures có giải thích/fix không cần training; 0/10 đạt điều kiện kết luận `MODEL_CAPABILITY` vì lỗi đều do policy, deterministic logic hoặc gold contract.
- Bottleneck thật: evidence sufficiency và quiz decision policy; rule hiện tại gần như `node exists + source metadata => GENERATE_QUIZ`, không phân biệt mention với definition và không phát hiện concept cạnh tranh.
- Relation failures cần chốt relation contract trước; current hard-coded relation map tạo edge dựa trên co-occurrence và gold set chưa nhất quán về inferred `used_for`.
- Đã tạo reports: `failure_case_inventory.md`, `relation_failure_analysis.md`, `false_generate_analysis.md`, `citation_failure_analysis.md`, `quiz_decision_failure_analysis.md`, `root_cause_summary.md`.
- Kết luận giữ nguyên: `MORE REAL DATA REQUIRED BEFORE DECISION`; không fine-tune, không train, không đổi prompt/model behavior trong diagnosis.

## 🚧 Synthetic Iteration 1 + real corpus audit — 2026-09-18
- Đã sửa gold contract công khai trong `gold_contract_audit.md`: 3 case (`CONCEPT_005`, `GROUNDING_003`, `RELATION_005`); không thay đổi quality bar.
- Đã thêm evidence sufficiency có cấu trúc, làm `DISAMBIGUATE` reachable, constraining relation evidence, canonical phrase matching, và post-generation quiz validation; không fine-tune/train/prompt change.
- Iteration 1 trên 26 synthetic cases: Concept F1 = 1.000; Relation F1 = 1.000; Source Recall = 1.000; Decision Accuracy = 1.000; false `GENERATE_QUIZ` = 0; false refusal = 0.
- Citation Accuracy = 0.692 và Unsupported Claim Rate = 0.308 vì 5 candidate quiz bị deterministic semantic validation giữ lại thay vì trả unsupported grounded output. Có 10 publishable quiz, structural/semantic score = 20/20 chỉ trên các quiz đã pass; không dùng con số này làm production quality.
- Full software suite sau thay đổi: 24 passed, 51 existing deprecation warnings.
- Real corpus audit: chưa có human-labeled gold; chỉ 1 lesson provisional (`lesson_06`) được mark included để annotate, các lesson còn lại bị exclude do duplicate source group, encoding corruption, missing IDs, zero chunks hoặc low-information extraction. Real metrics = unavailable/inconclusive.
- Reports mới: `gold_contract_audit.md`, `iteration_1.json`, `iteration_1.md`, `baseline_vs_iteration_1.md`, `final_summary.md`, `real_baseline.md`, `real_error_analysis.md`; manifest tại `evals/real/lesson_manifest.json`.
- Fine-tuning decision: `MORE REAL DATA REQUIRED BEFORE DECISION`; next step là re-ingest/correct real corpus, human-label 5–10 clean source groups và 30–60 quiz cases trước khi đánh giá module fine-tuning cụ thể.
