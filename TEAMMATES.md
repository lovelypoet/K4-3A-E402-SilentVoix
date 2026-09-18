# BÁO CÁO PHÂN CÔNG VAI TRÒ & ĐÓNG GÓP THÀNH VIÊN (TEAMMATES REPORT)

> **Dự án:** SilentVoix — Lesson Studio: Đồng Bộ Bài Giảng & Học Thích Ứng  
> **Repo:** `K4-3A-E402-SilentVoix`  
> **Khóa / Lớp / Phòng:** Batch 04 · Lớp 3A · Phòng E402  
> **Track:** Track C — Lesson Studio / Track D — Học tập thích ứng & tương tác  

---

## 👥 1. Danh Sách Thành Viên & Bảng Phân Công Tổng Quan

| STT | Họ và Tên | Mã Học Viên | Vai trò chính | Phân vùng Module phụ trách | Tỷ lệ đóng góp |
|:---:|---|:---:|---|---|:---:|
| 1 | **Nguyễn Đức Anh** | `2A202602508` | Leader / AI & Knowledge Graph Lead | Phụ trách Product Architecture, AI Spec, Concept Extraction, Relationship Extraction, Knowledge Graph, Anti-Hallucination Quiz Engine (`GENERATE_QUIZ`, `DISAMBIGUATE`, `REFUSE_UNGROUNDED`), Prompt Engineering & Golden Set AI Eval. | **25%** |
| 2 | **Nguyễn Như Tài** | `2A202602976` | Backend & Data Engineer | Phụ trách Data Ingestion (PDF, PPTX, YouTube, Subtitle/Transcript parsing), Chunking & Metadata, SQLite/JSON Persistent Storage, RESTful FastAPI APIs, và bộ công cụ Source Mapper 2 chiều (Slide/Timestamp ↔ Concept). | **25%** |
| 3 | **Lò Văn Long** | `2A202602541` | Frontend & UX Engineer | Phụ trách giao diện Lesson Studio UI, Slide Viewer, Video Viewer (YouTube Sync), Interactive SVG/D3.js Knowledge Graph Canvas, Đồng bộ 2 chiều Slide/Video ⇄ Graph, Citation UI và Lecturer Review UI. | **25%** |
| 4 | **Nguyễn Công Vinh** | `2A202602519` | Fullstack & Adaptive Learning Engineer | Phụ trách tích hợp Frontend–Backend, tính toán Concept Mastery, thuật toán duyệt đồ thị tìm Prerequisite, Đề xuất lộ trình ôn tập thích ứng (Adaptive Recommendation Engine), và bộ suite Integration/E2E testing. | **25%** |

---

## 🛠️ 2. Chi Tiết Phân Công & Sản Phẩm Đã Hoàn Thành Của Từng Thành Viên

### 1️⃣ Nguyễn Đức Anh — Leader / AI & Knowledge Graph Lead (`2A202602508`)

* **Ownership File / Folder:**
  - [`ai/pipeline.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/ai/pipeline.py) *(Entry point xây dựng đồ thị & quiz)*
  - [`ai/extraction/concept_extractor.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/ai/extraction/concept_extractor.py)
  - [`ai/extraction/normalizer.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/ai/extraction/normalizer.py) *(Deduplication & Alias normalization)*
  - [`ai/extraction/relationship_extractor.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/ai/extraction/relationship_extractor.py)
  - [`ai/quiz/generator.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/ai/quiz/generator.py) *(Bộ máy sinh Quiz chống hallucination)*
  - [`ai/grounding/verifier.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/ai/grounding/verifier.py)
  - [`spec.md`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/spec.md) *(Viết và hoàn thiện AI Spec)*
* **Đóng góp kĩ thuật nổi bật:**
  1. Xây dựng **AI Pipeline** bóc tách danh sách Khái niệm (`ConceptNode`) và Mối quan hệ (`prerequisite_of`, `used_for`) từ tài liệu thô.
  2. Phát triển **Anti-Hallucination Tri-State Decision Engine**:
     - `GENERATE_QUIZ`: Sinh câu hỏi trắc nghiệm kèm Citation nguồn khi có đủ bằng chứng trong bài giảng.
     - `DISAMBIGUATE`: Trả về yêu cầu làm rõ khi bằng chứng tài liệu nhập nhằng/có nhiều cách hiểu.
     - `REFUSE_UNGROUNDED`: **Từ chối sinh quiz tuyệt đối** khi yêu cầu kiến thức không có trong tài liệu gốc.
  3. Soạn thảo **Golden Set** (`eval/golden_set.json`) và bộ quy chuẩn đánh giá chất lượng AI.

---

### 2️⃣ Nguyễn Như Tài — Backend & Data Engineer (`2A202602976`)

* **Ownership File / Folder:**
  - [`adaptive_learning/ingestion.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/adaptive_learning/ingestion.py) *(Bóc tách PDF, PPTX, Subtitle/Transcript)*
  - [`adaptive_learning/source_mapper.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/adaptive_learning/source_mapper.py) *(Engine tra cứu 2 chiều)*
  - [`adaptive_learning/storage.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/adaptive_learning/storage.py) *(Quản lý lưu trữ kiên cố `data/storage.json`)*
  - [`adaptive_learning/models.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/adaptive_learning/models.py) *(Định nghĩa 9 Pydantic Data Schemas)*
  - [`adaptive_learning/api.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/adaptive_learning/api.py) *(FastAPI REST Endpoints Router)*
  - [`eval/test_be_modules.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/eval/test_be_modules.py) *(Unit test suite cho Backend)*
* **Đóng góp kĩ thuật nổi bật:**
  1. Xây dựng module **Document Ingestion**: Hỗ trợ bóc tách file PDF thật (`pypdf`), PPTX thật (`python-pptx`), và Video Transcript (`.srt`, `.vtt`, `.json`) mà **không làm mất metadata nguồn gốc** (`slide`, `start_time`, `end_time`).
  2. Thiết kế **Source Mapper Engine** thực hiện phép tra cứu 2 chiều tức thì:
     - `get_concepts_by_slide(slide_num)` $\to$ Trả về các Concept thuộc Slide.
     - `get_concept_by_time(timestamp)` $\to$ Trả về Concept thuộc giây Video.
     - `get_source_by_concept(concept_id)` $\to$ Trả về vị trí Slide/Video của Concept.
  3. Triển khai 10 RESTful API endpoints với FastAPI, tích hợp lưu trữ kiên cố (persistent storage) tự động khôi phục dữ liệu sau khi restart server.
  4. Viết unit test suite `test_be_modules.py` đạt điểm số tuyệt đối **5/5 PASSED**.

---

### 3️⃣ Lò Văn Long — Frontend & UX Engineer (`2A202602541`)

* **Ownership File / Folder:**
  - [`index.html`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/index.html) *(Giao diện Lesson Studio chính)*
  - [`fe/index.html`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/fe/index.html)
  - [`fe/scripts/graph.js`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/fe/scripts/graph.js) *(Render Knowledge Graph canvas SVG/D3.js)*
  - [`fe/scripts/video-player.js`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/fe/scripts/video-player.js) *(Tương tác Slide Viewer & YouTube Video Player)*
  - [`fe/scripts/quiz.js`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/fe/scripts/quiz.js) *(Giao diện Quiz & Citation nguồn)*
  - [`fe/scripts/app.js`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/fe/scripts/app.js) *(Điều phối UI & Đồng bộ 2 chiều)*
  - [`fe/styles/main.css`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/fe/styles/main.css) *(Thiết kế giao diện kem ấm sang trọng)*
* **Đóng góp kĩ thuật nổi bật:**
  1. Thiết kế giao diện **Lesson Studio UI** đẹp mắt, hiện đại, tối ưu trải nghiệm người dùng với theme kem sang trọng (Warm Cream UI).
  2. Lập trình **Interactive Knowledge Graph Canvas**: Cho phép người dùng kéo thả (pan), phóng to/thu nhỏ (zoom), và nhấp chọn Node khái niệm.
  3. Hiện thực hóa **Hero Feature — Đồng bộ 2 chiều (Bidirectional Sync)**:
     - Khi Slide/Video chạy $\to$ Node tương ứng trên Graph phát sáng.
     - Khi bấm vào Node trên Graph $\to$ Viewer tự động nhảy về đúng trang Slide hoặc giây Video tương ứng.
  4. Xây dựng Lecturer Review UI cho phép giảng viên duyệt, chỉnh sửa và xuất bản bài giảng.

---

### 4️⃣ Nguyễn Công Vinh — Fullstack & Adaptive Learning Engineer (`2A202602519`)

* **Ownership File / Folder:**
  - [`adaptive_learning/mastery.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/adaptive_learning/mastery.py) *(Thuật toán tính điểm Concept Mastery)*
  - [`adaptive_learning/graph.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/adaptive_learning/graph.py) *(Duyệt đồ thị tìm Prerequisite)*
  - [`fe/scripts/data-loader.js`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/fe/scripts/data-loader.js) *(Tích hợp gọi API Backend)*
  - [`eval/run_eval.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/eval/run_eval.py) *(Chạy 26 test cases evaluation suite)*
  - [`eval/run_e2e_eval.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/eval/run_e2e_eval.py) *(Chạy End-to-End Evaluation)*
  - [`tests/test_ai_pipeline.py`](file:///d:/vinuni%20AI/hackathon/K4-3A-E402-SilentVoix/tests/test_ai_pipeline.py) *(PyTest software tests)*
* **Đóng góp kĩ thuật nổi bật:**
  1. Phát triển **Thuật toán Concept Mastery**: Tính toán điểm năng lực có trọng số dựa trên lịch sử trả lời đúng/sai của học viên ($0.0 \to 1.0$).
  2. Xây dựng **Engine Đề xuất Học thích ứng (Adaptive Learning Recommendation)**:
     - Khi phát hiện khái niệm yếu ($Mastery < 0.5$) $\to$ duyệt ngược đồ thị tìm khái niệm tiên quyết (Prerequisite).
     - Kết nối với `SourceMapper` để tạo link gợi ý học viên xem lại đúng trang Slide / timestamp Video.
  3. Đảm nhận công tác **Tích hợp End-to-End Frontend–Backend**: Kết nối giao diện JavaScript với REST APIs.
  4. Thực thi và duy trì bộ kiểm thử toàn diện: **13/13 PyTest Passed**, **26/26 Evaluation Cases Passed**.

---

## 🔄 3. Hợp Đồng Tích Hợp Giữa Các Phân Hệ (Integration Contract)

```text
  [Nguyễn Như Tài - BE]                     [Nguyễn Đức Anh - AI Engine]
   Document / Transcript                     Raw Text Chunks & Metadata
            │                                             │
            ▼                                             ▼
  Chunking + Source Mapping ───────────────► Concept & Relation Extraction
            │                                             │
            ▼                                             ▼
  FastAPI Endpoints (/adaptive/*) ◄────────── Structured Knowledge Graph & Quiz
            │
            ├─────────────────────────────────────────────┐
            ▼                                             ▼
  [Lò Văn Long - FE UI]                     [Nguyễn Công Vinh - Adaptive]
  Render SVG Knowledge Graph                 Submit Answer & Update Mastery
  Slide / Video Player Sync                  Weak Concept & Prerequisite Traversal
  Interactive Selection                      Generate Targeted Recommendation Link
```

- **Backend $\leftrightarrow$ AI Engine Contract:** Backend gửi danh sách `Chunk` chứa `text`, `slide`, `start_time`; AI Engine trả về `GraphJSON` (`nodes`, `edges`) và `QuizJSON` kèm Citation.
- **Backend $\leftrightarrow$ Frontend Contract:** Frontend gọi các REST APIs chuẩn JSON:
  - `GET /adaptive/knowledge-graph/{lesson_id}`
  - `GET /adaptive/concepts/by-slide/{slide}`
  - `GET /adaptive/concepts/by-time/{timestamp}`
  - `POST /adaptive/quiz/answer`
- **Adaptive $\leftrightarrow$ Frontend Contract:** Engine tính điểm Mastery, trả về danh sách `RecommendationResponse` kèm vị trí Slide/Video cần tua đến.

---
