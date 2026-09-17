# Báo Cáo Tổng Kết: Adaptive Learning & Evaluation Framework

Tài liệu này tổng hợp toàn bộ giải pháp kỹ thuật, lý do thiết kế và kết quả minh chứng cho phân hệ **Adaptive Learning & Evaluation Framework** do vai trò _Full-stack / Adaptive Learning & Evaluation Engineer_ thực hiện.

---

## 1. Đã làm những gì?

- **Phân hệ Adaptive Learning**: Xây dựng thuật toán chấm điểm năng lực (Mastery Model), phân loại trạng thái học tập (Mastery State) và thuật toán dò tìm lỗ hổng kiến thức (Prerequisite Analysis). Đóng gói toàn bộ thành một API Recommendation.
- **Phân hệ Evaluation Framework**: Xây dựng một kịch bản test tự động (Automated Test Suite) để đo lường độ chính xác của logic thuật toán (Structured Diff) và chất lượng sư phạm của nội dung do AI sinh ra (LLM-as-Judge).

---

## 2. Làm bằng cách nào?

- **Kiến trúc Pure Functions**: Tách rời hoàn toàn logic tính điểm và dò đồ thị (`mastery.py`, `graph.py`) khỏi Database. Các hàm này chỉ nhận Input là List/Dict và trả về Output.
- **Thuật toán BFS (Breadth-First Search)**: Áp dụng BFS chạy ngược (backward traversal) trên Knowledge Graph để tìm ra khái niệm (concept) gần nhất bị hổng.
- **FastAPI Router**: Tạo file `api.py` bọc logic lại thành 1 endpoint `GET /adaptive/recommendation` trả về chuẩn JSON cho Frontend.
- **LLM-as-Judge**: Tích hợp SDK `google-genai` vào file `eval/llm_judge.py`. Dùng model `gemini-2.5-flash` đóng vai trò "Giám khảo". Ép kiểu dữ liệu trả về bằng Pydantic (`Response_Schema`) để luôn nhận được JSON chuẩn.

---

## 3. Tại sao lại dùng cách này?

- **Tại sao dùng Pure Functions?** Đảm bảo tính Deterministic (kết quả luôn nhất quán). Giúp phát triển và viết test siêu nhanh mà không bị "block" bởi tiến độ làm Database của Backend. Khi Backend làm xong DB, họ chỉ việc gọi hàm của ta là xong.
- **Tại sao dùng thuật toán BFS thay vì đệ quy sâu (DFS)?** Học viên thường muốn ôn lại kiến thức gần nhất bị quên trước khi phải học lại những kiến thức quá xa xôi ở gốc rễ. BFS quét theo từng tầng giúp tìm ra Prerequisite gần nhất. Đồng thời thuật toán có cơ chế chống lặp vô hạn (circular loop) nếu AI sinh Graph bị lỗi.
- **Tại sao dùng LLM-as-Judge?** Việc sinh ra Quiz hay trích xuất nội dung bằng ngôn ngữ tự nhiên không thể chấm điểm bằng code `if/else` hay so sánh chuỗi (string-matching). Việc dùng LLM chấm điểm với tham số `Temperature = 0.0` giúp tự động hóa khâu QA (Quality Assurance) mà vẫn đảm bảo tính khách quan, nhất quán, tiết kiệm hàng giờ test thủ công.

---

## 4. Kết quả chứng minh

- Môi trường chạy thành công, không gặp lỗi cấu trúc, chịu tải được các edge-cases (vòng lặp vô hạn, data rỗng, thiếu thư viện).
- **Automation:** Chỉ với một câu lệnh `python eval/run_eval.py`, hệ thống tự động quét và chấm điểm toàn bộ 26 test cases.
- **Coverage:** Đạt tỷ lệ Pass **100%** trên toàn bộ các Metrics (Đo lường năng lực, Logic đồ thị, Data Integrity, Chất lượng sư phạm LLM). Hệ thống sẽ in thẳng ra Terminal tỷ lệ % và lý do thất bại nếu có.

---

## 5. Danh sách Bộ 26 Golden Cases (Test Suite)

Dưới đây là chi tiết 26 test cases trải dài qua các module quan trọng nhất:

### A. Nhóm Logic Cốt Lõi (Structured & Algorithmic Tests)

**1. Mastery Calculation (4 cases)**

- `case_1`: Học viên chưa có lịch sử làm bài (Trả về rỗng, không phải 0).
- `case_2`: Trả lời đúng 100% (Đạt 1.0).
- `case_3`: Trả lời 1 đúng 1 sai (Đạt 0.5).
- `case_4`: Trả lời đúng câu dễ, sai câu khó (Weighted Average).

**2. Mastery State Classification (5 cases)**

- `case_5`: Đang học ở slide hiện tại (Luôn là "current").
- `case_6`: Chưa học (Trạng thái "not_learned").
- `case_7`: Dưới 0.5 điểm (Trạng thái "weak").
- `case_8`: Từ 0.5 đến 0.85 (Trạng thái "learning").
- `case_9`: Trên 0.85 (Trạng thái "mastered").

**3. Prerequisite Traversal - Dò Graph (7 cases)**

- `case_10`: Node bị hổng là node gốc, không có điều kiện tiên quyết.
- `case_11`: Có đúng 1 điều kiện tiên quyết bị yếu.
- `case_12`: Bỏ qua các điều kiện tiên quyết đã được "mastered".
- `case_13`: Xử lý nhiều điều kiện tiên quyết cùng yếu một cách deterministic.
- `case_14`: Chống treo máy khi Graph bị vòng lặp (A cần B, B cần A).
- `case_15`: Dò sâu nhiều tầng để tìm lỗ hổng gốc rễ.
- `case_16`: Khái niệm bắt đầu đã được master (không recommend gì).

**4. Recommendation API (2 cases)**

- `case_17`: Test luồng E2E cho học viên yếu (trả về đúng mapping slide/video).
- `case_18`: Test luồng E2E cho học viên giỏi (không trả về gợi ý nào).

**5. Data Integrity (2 cases)**

- `case_19`: Sinh lại graph không làm mất mapping bài giảng.
- `case_20`: Xóa bài giảng không để lại dữ liệu mồ côi (orphaned data).

### B. Nhóm Chất Lượng AI (LLM-as-Judge & Extraction)

**6. AI Evaluation (6 cases)**

- `case_21 (Groundedness)`: LLM chấm Pass vì câu hỏi Quiz bám sát nội dung Document.
- `case_22 (Citation)`: LLM chấm Fail vì nguồn trích dẫn trỏ sai số Slide của bài giảng.
- `case_23 (Quiz Quality)`: LLM chấm Pass vì câu hỏi ("Learning rate quá lớn dẫn đến hiện tượng gì?") rõ ràng, phương án nhiễu logic.
- `case_24 (Extraction)`: So sánh cấu trúc string normalized (VD: `Gradient Descent` khớp với `gradient descent`).
- `case_25 (Refusal)`: Đảm bảo AI trả về mã từ chối ("I don't know") đúng format khi không có dữ liệu.
- `case_26 (Sync)`: Đồng bộ chuẩn xác thời gian Video với Node tương ứng.
