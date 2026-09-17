# Backend — Phạm vi công việc & Danh sách API

> **Dự án:** Lesson Studio / SilentVoix  
> **Role:** Backend & Data Engineer  
> **Base URL:** `http://127.0.0.1:8000`  
> **Swagger:** `http://127.0.0.1:8000/docs`  
> **Code chính:** `adaptive_learning/api.py`, `ingestion.py`, `storage.py`, `models.py`, `source_mapper.py`, `graph.py`, `mastery.py`

---

## 1. BE làm gì?

Backend chịu trách nhiệm **dữ liệu + API**, không làm UI và không thay AI “hiểu bài”.

| Việc | Mô tả |
|------|--------|
| **Ingestion** | Nhận video link / slide link / file document → lưu, bóc text + metadata (`slide` hoặc `start_time`/`end_time`) |
| **Storage** | Lưu kiên cố vào `data/storage.json`, file binary vào `uploads/` |
| **Retrieval** | Trả lesson, slides, transcript, documents cho FE/AI |
| **Source mapping API** | Tra cứu concept theo slide / theo giây video |
| **Knowledge graph API** | Trả nodes + edges để FE vẽ đồ thị |
| **Quiz / Mastery** | Nhận đáp án, cập nhật mastery, recommendation theo BFS trên graph |

**Không thuộc BE:** click node seek video/slide (FE), extract concept/quan hệ đồ thị chất lượng cao (AI), thiết kế UI.

---

## 2. Luồng dữ liệu

```
[1 trong 3 nguồn]
  POST /lessons/video   → YouTube: transcript + timestamp
  POST /lessons/slide   → Google Docs/Slides/Drive public hoặc link file
  POST /upload          → file .pdf / .pptx / .docx

        ↓
  storage.json + uploads/
        ↓
  GET lessons / lesson detail / slides / documents
        ↓
  (AI đọc text → ghi concepts + source_mappings + prerequisites)
        ↓
  GET knowledge-graph / concepts/by-slide / concepts/by-time
        ↓
  FE vẽ graph, seek video/slide theo slide | start_time
```

Mỗi lesson chỉ có **một** `source_type`: `video` | `slide` | `document`.

---

## 3. Danh sách API

### 3.1. Nạp bài (POST) — đúng 1 trong 3

| Method | Path | Body | BE làm gì |
|--------|------|------|-----------|
| `POST` | `/adaptive/lessons/video` | `{ "video_url": "..." }` | Lưu link. YouTube → fetch transcript. TikTok/khác → chỉ lưu URL |
| `POST` | `/adaptive/lessons/slide` | `{ "slide_url": "..." }` | Lưu link. Docs/Slides/Drive **public** hoặc `.pdf/.pptx/.docx` → bóc tách. Private/Scribd → chỉ lưu URL |
| `POST` | `/adaptive/upload` | multipart `file` | Upload `.pdf` / `.pptx` / `.docx`, bóc text theo trang/slide |

### 3.2. Lấy dữ liệu bài giảng (GET)

| Method | Path | Trả về |
|--------|------|--------|
| `GET` | `/adaptive/lessons` | Danh sách tất cả lesson |
| `GET` | `/adaptive/lessons/{lesson_id}` | Chi tiết: URL, slides[], transcript[], concepts[] |
| `GET` | `/adaptive/lessons/{lesson_id}/slides/{slide_number}` | **Text thô** của 1 trang slide |
| `GET` | `/adaptive/documents` | Danh sách file đã upload |

### 3.3. Knowledge graph & Source mapper (GET)

| Method | Path | Trả về | Khác gì? |
|--------|------|--------|----------|
| `GET` | `/adaptive/knowledge-graph/{lesson_id}` | `nodes` + `edges` (concept + prerequisite). Node có `slide`, `start_time`, `end_time` | Để **vẽ graph** |
| `GET` | `/adaptive/concepts/by-slide/{slide_number}?lesson_id=` | Concepts gắn với **slide N** | Slide → concept |
| `GET` | `/adaptive/concepts/by-time/{timestamp_seconds}?lesson_id=` | Concept tại **giây video** | Video timeline → concept |

> `.../slides/{n}` = nội dung chữ trang đó  
> `.../concepts/by-slide/{n}` = khái niệm gắn trang đó  

### 3.4. Quiz & học thích ứng

| Method | Path | BE làm gì |
|--------|------|-----------|
| `POST` | `/adaptive/quiz/answer` | Ghi attempt, cập nhật mastery |
| `GET` | `/adaptive/recommendation/{student_id}?current_concept_id=` | BFS tìm concept yếu + trả `source` (slide/time) |
| `GET` | `/adaptive/mastery/{student_id}` | Bảng mastery theo concept |

### 3.5. Khác

| Method | Path | Mô tả |
|--------|------|--------|
| `GET` | `/` | Health check |
| Static | `/uploads/{filename}` | Serve file đã upload |

---

## 4. Request / Response mẫu nhanh

### Video
```http
POST /adaptive/lessons/video
Content-Type: application/json

{ "video_url": "https://www.youtube.com/watch?v=aircAruvnKk" }
```

### Slide / Docs link
```http
POST /adaptive/lessons/slide
Content-Type: application/json

{ "slide_url": "https://docs.google.com/document/d/FILE_ID/edit" }
```

### Document upload
```http
POST /adaptive/upload
Content-Type: multipart/form-data

file = BaiGiang.pdf
```

### Lesson detail
```http
GET /adaptive/lessons/lesson_02
```

### Knowledge graph
```http
GET /adaptive/knowledge-graph/lesson_02
```

---

## 5. File / module BE

| Module | Vai trò |
|--------|---------|
| `main.py` | FastAPI app, CORS, mount `/uploads` |
| `adaptive_learning/api.py` | Toàn bộ route `/adaptive/*` |
| `adaptive_learning/ingestion.py` | PDF/PPTX/DOCX, YouTube transcript, Google export |
| `adaptive_learning/storage.py` | CRUD `storage.json` |
| `adaptive_learning/models.py` | Pydantic schemas |
| `adaptive_learning/source_mapper.py` | Logic slide/time ↔ concept |
| `adaptive_learning/graph.py` | BFS prerequisite / recommendation |
| `adaptive_learning/mastery.py` | Tính điểm mastery |
| `data/storage.json` | DB file |
| `uploads/` | File document đã upload |
| `requirements.txt` | Dependencies |
| `eval/test_real_upload.py` | Test 3 POST ingest |

---

## 6. Phân biên role (để team rõ)

| Đã có từ BE | Việc tiếp theo |
|-------------|----------------|
| Text + timestamp/slide sau ingest | **AI** extract concept, edges, mapping chất lượng |
| Graph API có field `slide` / `start_time` | **FE** click node → seek video hoặc nhảy slide + hiện nội dung |
| Quiz answer + mastery | **AI** (tuỳ chọn) sinh câu hỏi; FE hiển thị |

---

## 7. Chạy server

```powershell
cd "d:\vinuni AI\hackathon\K4-3A-E402-SilentVoix"
pip install -r requirements.txt
python main.py
```

Mở: http://127.0.0.1:8000/docs
