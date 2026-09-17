# AI SPEC — Knowledge-to-Lesson: Synchronized Knowledge Graph & Grounded Quiz · Nhóm [XX] · Zone C

Hướng: [ ] A — VLearn  [ ] B — Trợ lý Học viên  [x] C — Làn mở

Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới


## §1. User & Job

### Job executor + workflow

**Primary user / Job executor:**  
Giảng viên / người biên soạn nội dung (Studio Team).

**Secondary user:**  
Học viên sử dụng bài học được tạo từ slide, transcript hoặc video.

### Workflow hiện tại

```text
Slide / Transcript / Video
        ↓
Giảng viên đọc và lọc nội dung
        ↓
Xác định các concept quan trọng
        ↓
Tự tổ chức thứ tự / quan hệ kiến thức
        ↓
Soạn quiz
        ↓
Kiểm tra lại quiz với tài liệu
        ↓
Xuất bản bài học
        ↓
Học viên học tuyến tính theo slide/video
        ↓
Khi không hiểu hoặc làm sai quiz
        ↓
Tự tìm lại phần kiến thức liên quan
```

Workflow hiện tại tạo ra hai nhóm pain chính:

**Phía giảng viên:** cần tổ chức kiến thức, thể hiện mối quan hệ giữa các phần của bài học, xây dựng câu hỏi và đảm bảo nội dung có thể kiểm chứng từ tài liệu.

**Phía học viên:** khó nhìn thấy mối quan hệ giữa các kiến thức, khó xác định kiến thức nền đang bị hổng và khó tìm lại đúng slide/đoạn video cần ôn.


### Core JTBD

> Khi chuẩn bị một bài học từ slide, transcript hoặc video, giảng viên muốn tổ chức các kiến thức chính, mối quan hệ giữa chúng và nguồn gốc của từng kiến thức để học viên có thể theo dõi bài học dễ hơn, đồng thời các nội dung kiểm tra có thể được kiểm chứng lại từ tài liệu gốc.


### Problem statement

Tài liệu học tập thường được trình bày tuyến tính theo slide hoặc timeline video. Điều này khiến việc tổ chức và truyền đạt mối quan hệ giữa các kiến thức mất công ở phía giảng viên, trong khi học viên khó nhận biết kiến thức hiện tại liên quan hoặc phụ thuộc vào kiến thức nào và khó tìm lại đúng nguồn cần ôn khi bị hổng.


### Evidence

Nhóm thực hiện validation ban đầu từ hai phía: học viên và giảng viên.


#### A. Khảo sát học viên — n = 9

Nhóm thực hiện khảo sát ban đầu với **9 học viên** đang tham gia các khóa học.

Kết quả:

- **8/9 (88,9%)** cho biết trong 1–2 tuần gần đây ít nhất thỉnh thoảng gặp khó khăn trong việc xác định các kiến thức/khái niệm liên quan hoặc phụ thuộc lẫn nhau.

- Trong đó **6/9 (66,7%)** cho biết tình trạng trên xảy ra **thường xuyên**.

- **8/9 (88,9%)** đánh giá việc không nắm rõ mối quan hệ giữa các kiến thức ảnh hưởng đến tiến độ học tập ở mức **3–4** trên thang khảo sát.

- **8/9 (88,9%)** cho biết khi làm sai quiz, họ ít nhất đôi khi gặp tình trạng không biết chính xác kiến thức nền tảng nào đang bị hổng.

- Trong đó **3/9 (33,3%)** cho biết tình trạng trên xảy ra **thường xuyên**.

- **8/9 (88,9%)** đánh giá công sức/thời gian phải tự tìm lại nguồn gốc của một đáp án hoặc kiến thức trong tài liệu dài ở mức **3–4**.

- Với câu hỏi về vấn đề gây phiền toái khi học từ tài liệu, **7/8 câu trả lời hợp lệ (87,5%)** chọn:

> “Khó kiểm chứng đáp án hoặc kiến thức xuất phát từ nguồn tài liệu nào.”

Kết quả khảo sát ban đầu cho thấy ba pain nổi bật:

```text
Không rõ quan hệ kiến thức
        +
Không biết kiến thức nền bị hổng
        +
Khó truy ngược về nguồn
```


#### B. Phỏng vấn giảng viên — n = 2

Nhóm đã thực hiện trao đổi/phỏng vấn ban đầu với **2 giảng viên**.

Cả hai giảng viên đều xác nhận nhu cầu về một tính năng hỗ trợ tổ chức và biểu diễn kiến thức nhằm:

- hỗ trợ việc giảng dạy và trình bày kiến thức dễ hơn;
- giúp học viên follow-up nội dung bài học dễ hơn;
- giúp học viên nhìn thấy mối liên hệ giữa các phần kiến thức thay vì chỉ tiếp nhận nội dung theo slide/video tuyến tính.

Đây là validation định tính ban đầu từ phía job executor.

Do số lượng phỏng vấn hiện tại mới là **n = 2**, nhóm chỉ sử dụng kết quả này như **early validation**, không xem đây là kết luận đại diện cho toàn bộ giảng viên.


### Quote / ví dụ nguyên văn + nguồn

**Quote 01 — Học viên:**

> “mình học 1 tiết học có 200 slide và đôi lúc mất tập trung mình bị trôi mất kiến thức”

Nguồn: Khảo sát trải nghiệm học tập và ôn tập tài liệu, 16/09/2026.

**Quote 02 — Giảng viên:**  
[TBD — bổ sung nguyên văn từ interview log]

**Quote 03 — Giảng viên:**  
[TBD — bổ sung nguyên văn từ interview log]

**Quote 04 — Học viên:**  
[TBD — bổ sung nguyên văn]

**Quote 05 — Học viên/Giảng viên:**  
[TBD — bổ sung nguyên văn]

> Lưu ý: nhóm không tự tạo hoặc diễn giải lại nội dung thành quote. Các vị trí TBD sẽ được thay bằng câu trả lời nguyên văn từ interview/survey log trước khi hoàn tất evidence.


---

## §2. Impact & quyết định chọn

### Bảng impact các ứng viên

| Ứng viên / Pain | Bao nhiêu người | Tần suất / mức độ | Tốn gì mỗi lần | Khả thi MVP |
|---|---:|---|---|---|
| Khó hiểu quan hệ/phụ thuộc giữa kiến thức | 8/9 học viên gặp ít nhất đôi khi | 6/9 gặp thường xuyên | Khó follow lesson, phải tự kết nối kiến thức | Cao |
| Khó truy ngược kiến thức về nguồn | 8/9 đánh giá công sức tìm nguồn mức 3–4; 7/8 valid responses chọn source verification là pain nổi bật | Khi cần kiểm chứng hoặc ôn lại | Tốn thời gian tìm slide/đoạn video | Cao |
| Không biết knowledge gap sau quiz | 8/9 gặp ít nhất đôi khi | 3/9 gặp thường xuyên | Không biết nên quay lại học phần nào | Trung bình–Cao |
| Tổ chức kiến thức phục vụ giảng dạy | 2/2 giảng viên được phỏng vấn xác nhận nhu cầu ban đầu | Theo quá trình chuẩn bị/giảng bài | Công sức tổ chức và giúp student follow-up | Cao |
| Quiz generation đơn thuần | Chưa có evidence cho thấy đây là pain lớn nhất | Theo mỗi lesson | Thời gian soạn câu hỏi | Rất cao |
| Adaptive Learning hoàn chỉnh | Có tín hiệu learner-side nhưng chưa đủ longitudinal data | Sau nhiều lượt học | Cần theo dõi learner state | Trung bình–Thấp ở MVP |


### Ứng viên ĐÃ LOẠI

#### Quiz Generator đơn thuần

Nhóm không chọn quiz generation đơn thuần làm lát cắt chính.

Lý do: quiz generation chỉ giải quyết việc tạo câu hỏi nhưng không trực tiếp giải quyết ba pain đã xuất hiện trong validation:

1. Không nhìn thấy relationship giữa kiến thức.
2. Không biết knowledge gap sau khi trả lời sai.
3. Khó truy ngược kiến thức/đáp án về nguồn.

Quiz generation vẫn được giữ lại nhưng trở thành một chức năng được **grounded trên Knowledge Graph và source**.


#### Adaptive Learning hoàn chỉnh

Nhóm chưa chọn Adaptive Learning hoàn chỉnh làm core MVP.

Adaptive Learning đầy đủ cần lượng dữ liệu tương tác của học viên đủ lớn và theo thời gian để xây dựng/đánh giá learner model.

Trong MVP, nhóm chỉ triển khai vòng lặp đơn giản:

```text
Quiz Result
     ↓
Weak Concept
     ↓
Prerequisite
     ↓
Recommended Source
```


### Ứng viên CHỌN

Nhóm chọn:

> **Synchronized Knowledge Graph + Source Grounding + Grounded Quiz**

làm lát cắt chính.

Evidence ban đầu:

- **8/9** học viên gặp pain liên quan đến relationship giữa kiến thức.
- **8/9** ít nhất đôi khi không biết knowledge gap sau quiz.
- **8/9** đánh giá việc tìm lại nguồn tốn công ở mức 3–4.
- **7/8 câu trả lời hợp lệ** chọn khó kiểm chứng nguồn là pain nổi bật.
- **2/2 giảng viên được phỏng vấn ban đầu** xác nhận nhu cầu hỗ trợ teaching và student follow-up.

Knowledge Graph được chọn làm semantic layer trung tâm vì một cấu trúc có thể kết nối:

```text
Knowledge Structure
        +
Semantic Navigation
        +
Source Traceability
        +
Grounded Quiz
        +
Prerequisite-based Review
```


---

## §3. Giải pháp tương tự đã nghiên cứu

### NotebookLM

**Flow tham khảo:**

```text
Upload Sources
      ↓
Grounded Interaction
      ↓
Answer / Summary
      ↓
Source Reference
```

**Đáng học:**

- Grounding dựa trên tài liệu người dùng cung cấp.
- Cho phép truy ngược output về source.
- Tăng khả năng kiểm chứng nội dung được sinh ra.

**Đáng né:**

Nhóm không muốn sản phẩm chỉ trở thành giao diện hỏi đáp hoặc tóm tắt tài liệu.

**Nhóm khác gì:**

Knowledge Graph được sử dụng như một **semantic navigation layer** của lesson:

```text
Slide / Video
      ⇅
Knowledge Graph
```

Graph không chỉ là visualization mà còn kết nối concept với vị trí thực tế trong lesson.


### Quizlet

**Flow tham khảo:**

```text
Learning Material
       ↓
Learning Activities
       ↓
Quiz / Practice
```

**Đáng học:**

- Learning interaction đơn giản.
- Quiz/practice được đưa trực tiếp vào quá trình học.

**Đáng né:**

Không lấy automatic quiz generation làm toàn bộ value proposition.

**Nhóm khác gì:**

Mỗi quiz được liên kết theo cấu trúc:

```text
Quiz
 ↓
Concept
 ↓
Evidence
 ↓
Slide / Page / Timestamp
```

Kết quả quiz có thể tiếp tục cập nhật trạng thái của concept và hỗ trợ learner tìm phần kiến thức cần ôn.


---

## §4. Thiết kế

### Lát cắt MỘT CÂU

> **Một giảng viên cần chuyển slide/video thành một lesson có cấu trúc → hệ thống trích xuất concept và relationship, kiểm tra evidence để quyết định `GENERATE_QUIZ`, `DISAMBIGUATE` hoặc `REFUSE_UNGROUNDED` → mỗi concept/quiz được ánh xạ về đúng slide/timestamp → giảng viên kiểm tra trước khi publish và học viên có thể follow lesson thông qua Knowledge Graph đồng bộ với nguồn.**


### Non-goals

MVP **KHÔNG** tập trung vào:

1. Train foundation model từ đầu.
2. Xây dựng LMS hoàn chỉnh.
3. Xây Deep Knowledge Tracing/Bayesian Knowledge Tracing hoàn chỉnh.
4. Fully automate việc publish nội dung mà không có lecturer review.
5. Sử dụng kiến thức ngoài source rồi trình bày như grounded knowledge.
6. Xây chatbot general-purpose.
7. Xây production-scale distributed architecture.


### Mức prototype nhắm tới

[ ] Sketch  
[ ] Mock  
[x] Working


### Phần Working

AI/Knowledge Graph MVP:

```text
Structured Chunks
        ↓
Concept Extraction
        ↓
Concept Normalization
        ↓
Relationship Extraction
        ↓
Knowledge Graph
        ↓
Source Grounding
        ↓
Grounded Quiz
```

Trạng thái kỹ thuật hiện tại:

- Python 3.12.10.
- Package AI chính nằm trong `ai/`.
- Entry point: `ai.pipeline`.
- Đã thiết lập `.venv`.
- Đã có schema, extraction, graph, grounding và quiz.
- Đã có test/golden-set infrastructure ban đầu.
- AI demo graph/quiz/refusal chạy end-to-end.
- Software test hiện tại: **13 pytest passed**.


### Phần chưa hoàn thiện

- Baseline AI evaluation trên golden set hoàn chỉnh.
- Evaluation trên dữ liệu slide/transcript thực tế.
- Error analysis AI.
- Slide/Video ⇄ Knowledge Graph frontend synchronization hoàn chỉnh.
- Lecturer Review UI.
- Full frontend/backend/AI integration.
- Concept mastery + prerequisite recommendation loop hoàn chỉnh.
- Validation working prototype với user.


### Automation

[x] augment  
[ ] conditional  
[ ] automate


### Lý do theo cost-of-error

AI đề xuất cấu trúc kiến thức và quiz nhưng **giảng viên giữ quyền quyết định cuối cùng**.

```text
AI Proposal
     ↓
Lecturer Review
     ↓
Approve / Edit / Reject
     ↓
Publish
```

Một concept, relationship hoặc quiz sai có thể khiến học viên hiểu sai nội dung.

Do đó chi phí để giảng viên review trước khi publish thấp hơn chi phí sửa lỗi sau khi nội dung sai đã được sử dụng trong quá trình học.

Nhóm vì vậy chọn **Augment / Human-in-the-loop** thay vì Fully Automated Publishing.


### §4b. Nguyên tắc đã áp dụng

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| Make clear what the system can do | Chỉ tuyên bố nội dung grounded khi tìm được evidence trong source |
| Make clear how well the system can do | Software test và AI quality evaluation được báo cáo riêng |
| Support efficient correction | Lecturer có thể Approve/Edit/Reject nội dung trước publish |
| Scope services when in doubt | Evidence mơ hồ → `DISAMBIGUATE`; không có evidence → `REFUSE_UNGROUNDED` |
| Show contextually relevant information | Concept/quiz giữ citation tới slide/page/timestamp |
| Support graceful failure | Không đủ evidence thì không silently hallucinate |
| Preserve user control | AI augment quá trình authoring; user giữ quyền publish |
| Explain why | Quiz/recommendation có concept và source để user truy ngược |


---

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản

| Lớp lỗi | Kịch bản | Expected behavior |
|---|---|---|
| Input | PDF/slide không extract được text | Báo thiếu dữ liệu, không tạo graph giả |
| Input | Transcript không có timestamp | Có thể extract concept nhưng không cam kết video navigation chính xác |
| Input | Chunk bị thiếu metadata nguồn | Không coi output là fully grounded cho tới khi source được xác định |
| Concept | Một concept xuất hiện dưới nhiều tên | Normalize/merge khi đủ evidence |
| Concept | Hai thuật ngữ giống tên nhưng khác nghĩa | Không merge chỉ dựa trên lexical similarity |
| Concept | Model extract quá nhiều noun thành concept | Loại các candidate không phải meaningful learning concept |
| Relationship | Hai concept cùng xuất hiện nhưng không có quan hệ rõ | Không tự tạo strong relationship |
| Relationship | Nhầm hướng `prerequisite_of` | Evaluation fail / không chấp nhận edge |
| Relationship | Không chắc `prerequisite_of` hay `related_to` | Không khẳng định relation mạnh nếu evidence chưa đủ |
| Grounding | Concept hợp lý nhưng không tồn tại trong source | Không trình bày như grounded concept |
| Grounding | Citation trỏ sai slide/chunk | Case fail |
| Grounding | Timestamp không chứa evidence | Case fail |
| Quiz | Concept không tồn tại trong tài liệu | `REFUSE_UNGROUNDED` |
| Quiz | Evidence tồn tại nhưng có nhiều cách hiểu | `DISAMBIGUATE` |
| Quiz | Evidence đầy đủ | `GENERATE_QUIZ` kèm citation |
| Runtime | Slide/video không map được concept | Không highlight node giả |
| Runtime | Một concept xuất hiện ở nhiều source | Giữ nhiều source references |
| Adaptive | Không tìm thấy prerequisite | Không tạo prerequisite giả; trả về recommendation giới hạn theo evidence hiện có |


---

## §6. Bốn đường đi của trải nghiệm

### Happy path

```text
Giảng viên đưa tài liệu
        ↓
Document Ingestion
        ↓
Structured Chunks
        ↓
Concept Extraction
        ↓
Knowledge Graph
        ↓
Concept ↔ Source Mapping
        ↓
Evidence đủ
        ↓
GENERATE_QUIZ
        ↓
Lecturer Review
        ↓
Publish
        ↓
Student học với Slide/Video ⇄ Graph
```


### Low-confidence (②)

Hệ thống tìm thấy concept nhưng evidence hoặc relationship chưa đủ rõ:

```text
Ambiguous Evidence
        ↓
DISAMBIGUATE
        ↓
Hiển thị context/source liên quan
        ↓
User xác nhận / chỉnh sửa
```

Hệ thống không biến uncertainty thành một output chắc chắn.


### Failure / không căn cứ (①)

Ví dụ tài liệu chỉ có:

```text
Gradient Descent
SGD
Loss Function
```

User yêu cầu:

> “Generate a grounded quiz about AdamW.”

Expected behavior:

```text
REFUSE_UNGROUNDED
```

Hệ thống không sử dụng general pretrained knowledge về AdamW rồi trình bày nó như thông tin lấy từ tài liệu.


### Correction — user sửa

Lecturer có thể:

```text
AI Output
   ↓
Approve
  /   \
Edit  Reject
```

User không bắt buộc phải chấp nhận output AI ban đầu.

Các correction có thể bao gồm:

- sửa tên concept;
- merge/split concept;
- sửa relationship;
- sửa quiz;
- reject quiz;
- chọn lại citation/source.


### Khi bị đòi ngoài phạm vi (③)

Ví dụ:

> “Tài liệu nói AdamW tốt hơn SGD đúng không?”

Nếu tài liệu không chứa claim này, hệ thống:

```text
REFUSE_UNGROUNDED
```

hoặc yêu cầu user cung cấp thêm source.

Không tự dùng kiến thức bên ngoài để trả lời như thể claim tồn tại trong lesson.


### Case đặc thù domain (④)

Một concept có thể xuất hiện nhiều lần:

```text
Gradient Descent
├── Slide 17
├── Slide 21
├── Video 12:22
└── Video 18:05
```

Hệ thống giữ **một concept node với nhiều source references**.

Khi user click node, hệ thống điều hướng tới occurrence phù hợp hoặc cho phép lựa chọn source.


### Bidirectional experience

#### Slide/Video → Graph

```text
currentSlide / currentTime
           ↓
      Source Mapper
           ↓
     Active Concept
           ↓
     Highlight Node
```

#### Graph → Slide/Video

```text
User clicks Concept
          ↓
      Source Mapping
          ↓
Slide Number / Timestamp
          ↓
Viewer navigates to source
```


---

## §7. Kiểm thử

### 7.1 Chiều chất lượng

AI quality được đánh giá riêng với software correctness.


### A. Concept Extraction

**Định nghĩa đạt:**

Concept được extract phải tương ứng với meaningful learning concept trong source.

Metrics:

- Precision
- Recall
- F1


### B. Relationship Extraction

Một relationship được xem là đúng khi:

- đúng source concept;
- đúng target concept;
- đúng relation type;
- đúng direction;
- có evidence phù hợp.

Metrics:

- Precision
- Recall
- F1


### C. Grounding

Output được xem là grounded khi citation/source thực sự hỗ trợ claim hoặc quiz được tạo.

Metrics:

- Citation Accuracy
- Source Recall
- Unsupported Claim Rate


### D. Quiz Decision

Hệ thống phải lựa chọn đúng một trong ba decision:

```text
GENERATE_QUIZ
DISAMBIGUATE
REFUSE_UNGROUNDED
```

Metrics:

- Accuracy
- Precision
- Recall
- F1 theo từng decision class


### E. Refusal / Hallucination

Hệ thống phải từ chối khi source không hỗ trợ yêu cầu.

Metrics:

- Refusal Precision
- Refusal Recall
- Refusal F1
- Unsupported Generation Rate
- False Refusal Rate


### Golden Set

Golden set phải có tối thiểu **20 cases** và được lưu trong `eval/` hoặc `evals/` của repository.

Cơ cấu bao gồm:

1. Normal concept extraction.
2. Multiple concepts.
3. Duplicate concept / alias.
4. Similar-but-different concepts.
5. Cross-chunk concept.
6. Cross-slide concept.
7. Timestamped concept.
8. Valid relationship.
9. Ambiguous relationship.
10. Wrong relationship direction.
11. Unsupported relationship.
12. Valid citation.
13. Wrong citation.
14. Missing evidence.
15. Unsupported concept.
16. Valid grounded quiz.
17. Ambiguous quiz request.
18. Adversarial unsupported request.
19. Empty input.
20. Malformed/partial source metadata.


### Quality bar

Quality bar được chốt tại thời điểm nộp spec và không thay đổi chỉ để phù hợp với kết quả evaluation sau đó.

> **MVP được coi là đạt khi ≥80% case trong Golden Set đáp ứng expected behavior, Citation Accuracy ≥90%, và không có critical case nào tạo nội dung được tuyên bố là grounded khi source hoàn toàn không hỗ trợ.**

### Critical failure

Critical failure được định nghĩa là:

```text
Không có supporting evidence
            ↓
Hệ thống vẫn generate nội dung
            ↓
Nội dung được trình bày như grounded
```

Đây là loại lỗi nhóm ưu tiên tránh do ảnh hưởng trực tiếp đến độ tin cậy của nội dung giáo dục.


### Kết quả các lượt chạy

| Lượt | Version | Dataset | Pass rate | Citation Accuracy | Critical unsupported-grounded | Trạng thái |
|---|---|---|---:|---:|---:|---|
| Software Test | Current MVP | 13 pytest tests | 13/13 | N/A | N/A | Completed |
| AI Baseline | Current pretrained/zero-shot pipeline | ≥20 golden cases | TBD | TBD | TBD | Chưa chạy/chưa chốt |
| Iteration 1 | Prompt/Few-shot/Validation | Same evaluation set | TBD | TBD | TBD | Planned |
| Final pre-CP6 | Best validated MVP | Same quality bar | TBD | TBD | TBD | Planned |

**Lưu ý:** `13/13 pytest passed` chỉ chứng minh software pipeline hoạt động theo test hiện tại, không được sử dụng để kết luận AI đạt quality bar.


### Chiến lược cải thiện AI

Nhóm sử dụng quy trình:

```text
Pretrained Baseline
        ↓
Golden-set Evaluation
        ↓
Error Analysis
        ↓
Prompt Engineering
        ↓
Few-shot Examples
        ↓
Normalization / Rules / Validation
        ↓
Re-evaluation
        ↓
Fine-tune nếu thực sự cần
```


### Quyết định về Fine-tuning

Nhóm **không mặc định fine-tune model trong MVP**.

Fine-tuning chỉ được cân nhắc khi:

1. Một component không đạt quality bar.
2. Failure có pattern lặp lại.
3. Prompt/few-shot/rule-based validation không giải quyết đủ.
4. Có đủ annotated data chất lượng.
5. Improvement có thể được kiểm chứng trên held-out evaluation set.

Ví dụ các component có thể trở thành candidate trong tương lai:

- Concept Extraction.
- Relationship Classification.
- Concept Normalization / Embedding.
- Adaptive Learning / Knowledge Tracing.

Nếu failure đến từ:

- source metadata bị mất;
- chunking sai;
- mapping sai;
- API/data contract sai;

thì được xem là **engineering/data problem**, không phải lý do để fine-tune model.


---

## §8. Phân công & kế hoạch

### Nguyễn Đức Anh — Leader / Product Lead / AI & Knowledge Graph Engineer

Phụ trách:

- Spec.
- Product/AI architecture.
- Concept Extraction.
- Concept Normalization/Deduplication.
- Relationship Extraction.
- Knowledge Graph Construction.
- Source Grounding.
- Grounded Quiz.
- `GENERATE_QUIZ`.
- `DISAMBIGUATE`.
- `REFUSE_UNGROUNDED`.
- Prompt engineering.
- Golden-set AI evaluation.
- Baseline evaluation.
- Error analysis.
- Quyết định fine-tuning dựa trên evaluation evidence.
- Demo coordination.


### Nguyễn Như Tài — Backend & Data Engineer

Phụ trách:

- Document ingestion.
- PDF/slide/transcript processing.
- Chunking.
- Source metadata.
- Database.
- Knowledge Graph persistence.
- Concept ↔ Slide mapping.
- Concept ↔ Timestamp mapping.
- Backend APIs.
- Quiz/student data APIs.
- Data integrity tests.


### Lò Văn Long — Frontend / Knowledge Graph UX Engineer

Phụ trách:

- Lesson Studio UI.
- Slide Viewer.
- Video Viewer.
- Knowledge Graph visualization.
- Zoom/pan/select.
- Slide → Graph synchronization.
- Video → Graph synchronization.
- Graph → Slide/Video navigation.
- Active concept visualization.
- Citation navigation.
- Lecturer Review UI.
- Quiz UI.
- Mastery visualization.


### Nguyễn Công Vinh — Full-stack / Adaptive Learning & Evaluation Engineer

Phụ trách:

- Frontend/backend integration.
- Quiz → Concept mapping.
- Concept mastery.
- Weak concept detection.
- Prerequisite traversal.
- Learning recommendation.
- Integration tests.
- End-to-end tests.
- Adaptive-learning evaluation.


### Integration contract

```text
Nguyễn Như Tài
Document / Source
       ↓
Structured Chunks
       ↓
Nguyễn Đức Anh
AI / Knowledge Graph
       ↓
Graph + Sources + Quiz
       ↓
Backend Contract
     ↙         ↘
Lò Văn Long   Nguyễn Công Vinh
UI / Sync     Adaptive / Integration
     ↘         ↙
       End-to-End
```


### Willing users + kế hoạch validation

Validation ban đầu:

- **9 học viên** tham gia khảo sát.
- **2 giảng viên** tham gia trao đổi/phỏng vấn.

Willing users cho vòng working-prototype:

- **[Tên willing user 01] — [Vai trò]**
- **[Tên willing user 02] — [Vai trò]**

Nếu chương trình yêu cầu tên cụ thể, nhóm sẽ điền tên người đã đồng ý tham gia vòng prototype validation.


### Validation với giảng viên

Flow:

```text
Upload Lesson
      ↓
Review Knowledge Graph
      ↓
Generate Quiz
      ↓
Check Citation
      ↓
Approve / Edit / Reject
```

Quan sát:

- Concept có phù hợp cách giảng viên tổ chức bài không?
- Relationship có hợp lý không?
- Graph có giúp trình bày lesson không?
- Citation có giúp kiểm chứng output không?
- Bao nhiêu output cần Edit/Reject?
- Giảng viên có muốn sử dụng workflow này cho lesson tiếp theo không?


### Validation với học viên

Flow:

```text
Video / Slide
      ⇅
Knowledge Graph
      ↓
Quiz
      ↓
Weak Concept
      ↓
Prerequisite
      ↓
Source
```

Quan sát:

- Học viên có hiểu graph không?
- Có xác định được concept đang học không?
- Có tìm lại đúng kiến thức nhanh hơn không?
- Graph synchronization có giúp follow lesson không?
- Recommendation có dễ hiểu và hữu ích không?


### Multi-prototype

Nếu đủ thời gian, nhóm so sánh hai phương án.


#### Prototype A — Static Knowledge Graph

```text
Lesson
  ↓
Complete Knowledge Graph
```

Graph hiển thị toàn bộ lesson ngay từ đầu và không thay đổi theo tiến trình slide/video.


#### Prototype B — Synchronized / Progressive Knowledge Graph

```text
currentSlide / currentTime
          ↓
     Source Mapper
          ↓
    Active Concepts
          ↓
Knowledge Graph State
```

Graph highlight/reveal concept tương ứng với tiến trình lesson.

Đồng thời:

```text
Graph Node
    ↓
Source Mapping
    ↓
Slide / Timestamp
```

### Trục khác biệt

> **Static visualization vs. synchronized semantic navigation.**

Prototype B là hướng chính của nhóm vì nó trực tiếp kiểm chứng hypothesis rằng Knowledge Graph có thể giúp học viên follow và tìm lại kiến thức trong lesson dài.


---

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 16/09/2026 | Thực hiện khảo sát học viên ban đầu | Kiểm chứng pain về knowledge relationship, knowledge gap và source traceability |
| 17/09/2026 | Bổ sung validation từ 2 giảng viên | Kiểm chứng nhu cầu từ phía teaching/job executor |
| 17/09/2026 | Chọn Knowledge Graph làm semantic layer trung tâm | Một graph có thể kết nối concept, source, quiz và prerequisite |
| 17/09/2026 | Chọn Synchronized Knowledge Graph làm hero interaction | Giải quyết trực tiếp việc follow và tìm lại kiến thức trong slide/video dài |
| 17/09/2026 | Chọn Augment thay vì Automate | Cost-of-error của educational content cao; lecturer cần quyền kiểm soát |
| 17/09/2026 | Thêm Lecturer Review | Cho phép Approve/Edit/Reject trước publish |
| 17/09/2026 | Thêm `DISAMBIGUATE` | Không ép hệ thống trả lời chắc chắn khi evidence mơ hồ |
| 17/09/2026 | Thêm `REFUSE_UNGROUNDED` | Ngăn sử dụng general knowledge như thể đến từ source |
| 17/09/2026 | Tách software testing khỏi AI evaluation | Pipeline chạy đúng không đồng nghĩa semantic output đủ tốt |
| 17/09/2026 | Chốt Quality Bar trước baseline | Tránh thay threshold sau khi đã biết kết quả |
| 17/09/2026 | Chưa fine-tune model | Cần baseline và error analysis để xác định bottleneck trước khi training |


---

# MVP Definition of Done

MVP được coi là hoàn thiện khi có thể demo end-to-end flow:

```text
Educational Material
        ↓
Structured Chunks
        ↓
Concept Extraction
        ↓
Knowledge Graph
        ↓
Source Mapping
        ↓
Slide / Video ⇄ Knowledge Graph
        ↓
Grounded Quiz
        ↓
Lecturer Review
        ↓
Student Answer
        ↓
Concept Mastery
        ↓
Weak Prerequisite
        ↓
Recommended Slide / Timestamp
```

Hero demo cần thể hiện được:

1. Mở một lesson.
2. Slide/video chạy.
3. Knowledge Graph hiển thị các concept.
4. Khi slide/video thay đổi, active concept trên graph thay đổi tương ứng.
5. Click một concept trên graph.
6. Viewer điều hướng về đúng slide/timestamp chứa concept.
7. Generate quiz từ concept.
8. Quiz có citation/source.
9. Yêu cầu concept ngoài source → `REFUSE_UNGROUNDED`.
10. Trả lời quiz.
11. Concept mastery được cập nhật.
12. Nếu learner yếu ở concept, hệ thống tìm prerequisite và đưa về đúng source cần ôn.


---

# Current Project Status at Spec Freeze

Tại thời điểm chốt spec:

### Đã hoàn thành

- [x] `.venv` và dependencies.
- [x] Structured chunk schema.
- [x] Concept extraction pipeline.
- [x] Concept normalization.
- [x] Relationship extraction.
- [x] Knowledge Graph JSON.
- [x] Source grounding.
- [x] Grounded quiz.
- [x] `GENERATE_QUIZ`.
- [x] `DISAMBIGUATE`.
- [x] `REFUSE_UNGROUNDED`.
- [x] AI demo end-to-end cơ bản.
- [x] Software tests hiện tại: 13 pytest passed.
- [x] Survey learner-side ban đầu: n = 9.
- [x] Interview/validation giảng viên ban đầu: n = 2.


### Chưa hoàn thành

- [ ] ≥5 verbatim evidence quotes trong repo.
- [ ] Golden Set ≥20 AI-quality cases hoàn chỉnh.
- [ ] Baseline AI evaluation.
- [ ] Concept F1 baseline.
- [ ] Relationship F1 baseline.
- [ ] Citation Accuracy baseline.
- [ ] Refusal/Quiz Decision metrics.
- [ ] Error analysis.
- [ ] Evaluation trên dữ liệu lesson thực.
- [ ] Slide/Video ⇄ Knowledge Graph integration hoàn chỉnh.
- [ ] Lecturer Review UI hoàn chỉnh.
- [ ] Concept Mastery loop hoàn chỉnh.
- [ ] Prerequisite recommendation hoàn chỉnh.
- [ ] Working-prototype user validation.
- [ ] Final end-to-end integration test.


---

# Core Product Principle

> **AI biết mình đang dạy kiến thức nào, kiến thức đó đến từ đâu, và học viên đang thiếu phần nào.**

Lesson Studio không chỉ generate nội dung.

Knowledge Graph đóng vai trò là semantic layer kết nối:

```text
             SOURCE
               │
               ▼
          KNOWLEDGE GRAPH
          /      │       \
         /       │        \
   Navigation   Quiz     Mastery
       │         │          │
       ▼         ▼          ▼
 Slide/Video  Citation   Recommendation
```

Mục tiêu của MVP là chứng minh rằng cấu trúc này có thể giúp giảng viên tạo nội dung có khả năng kiểm chứng và giúp học viên follow, tìm lại và kết nối kiến thức tốt hơn trong một lesson.