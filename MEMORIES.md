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
## ➡️ Bước tiếp theo:
1. Khi có dữ liệu thật, bổ sung ingestion/evaluation thực tế; sau đó xử lý warning Pydantic/Starlette.
