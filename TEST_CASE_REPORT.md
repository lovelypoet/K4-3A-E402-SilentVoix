# Báo cáo kết quả kiểm thử AI và Adaptive Learning

## Nguồn kết quả và phạm vi

Báo cáo tổng hợp nguyên trạng output người dùng cung cấp từ lệnh:

```powershell
python eval/run_ai_e2e.py
```

Bộ kiểm thử gồm **22 cases**. Báo cáo này không chạy lại suite và không xác nhận kết quả thuộc commit nào. Tại thời điểm tạo báo cáo, không tìm thấy `eval/run_ai_e2e.py` trong workspace để đối chiếu implementation hiện tại; diễn giải phạm vi metric dựa trên runner đã trao đổi trong phiên và output được cung cấp.

## Kết quả chính

- **11 kiểm tra FAIL trên 10 case khác nhau**; `case_16` có hai kiểm tra fail.
- Concepts đạt **16/22 (72,73%)**; relationships đạt **19/22 (86,36%)**; quiz decision đạt **20/22 (90,91%)**.
- Source metadata và refusal cho concept không tồn tại đạt **22/22** mỗi metric.
- Các bước cấu trúc quiz, citation, mastery, weak state, recommendation và API đích đạt **21/21 lần thực thi** mỗi metric.
- Semantic groundedness bị **BLOCKED 21**; browser click bị **BLOCKED 22**.
- Không có ERROR trong output cung cấp. **Chưa đủ bằng chứng kết luận E2E production đạt.**

Không gộp các metric thành một tỷ lệ “đúng toàn hệ thống”: số lần áp dụng khác nhau và các bước bắt buộc còn BLOCKED.

## Bảng tổng hợp metric

Tỷ lệ đạt khi đã thực thi = PASS / (PASS + FAIL + ERROR). BLOCKED không được tính là PASS. Cột “Không có bản ghi” chỉ thể hiện chênh lệch so với 22 cases, không tự chuyển thành N/A.

| Metric | PASS | FAIL | BLOCKED | ERROR | Không có bản ghi | Tỷ lệ đạt đã thực thi |
|---|---:|---:|---:|---:|---:|---:|
| concepts | 16 | 6 | 0 | 0 | 0 | 72,73% |
| relationships | 19 | 3 | 0 | 0 | 0 | 86,36% |
| sources | 22 | 0 | 0 | 0 | 0 | 100% |
| quiz_decision | 20 | 2 | 0 | 0 | 0 | 90,91% |
| unsupported_refusal | 22 | 0 | 0 | 0 | 0 | 100% |
| quiz_structure | 21 | 0 | 0 | 0 | 1 | 100% |
| quiz_citations | 21 | 0 | 0 | 0 | 1 | 100% |
| semantic_groundedness | 0 | 0 | 21 | 0 | 1 | Chưa xác định |
| mastery | 21 | 0 | 0 | 0 | 1 | 100% |
| weak_state | 21 | 0 | 0 | 0 | 1 | 100% |
| recommendation_concept | 21 | 0 | 0 | 0 | 1 | 100% |
| recommendation_source | 21 | 0 | 0 | 0 | 1 | 100% |
| destination_api | 21 | 0 | 0 | 0 | 1 | 100% |
| browser_click | 0 | 0 | 22 | 0 | 0 | Chưa xác định |
| refusal_payload | 1 | 0 | 0 | 0 | 21 | 100% |

## Ý nghĩa từng metric và giới hạn

| Metric | Nội dung kiểm tra |
|---|---|
| concepts | So sánh danh sách concept ID thực tế với expected; dư concept cũng fail nếu so khớp chính xác |
| relationships | So sánh cạnh, hướng cạnh và loại quan hệ với expected; cạnh dư cũng có thể gây fail |
| sources | Concept có nguồn metadata khớp document/slide expected; không chứng minh nội dung concept đúng về nghĩa |
| quiz_decision | Quyết định GENERATE_QUIZ, REFUSE_UNGROUNDED hoặc DISAMBIGUATE đúng expected |
| unsupported_refusal | Từ chối khi yêu cầu concept không có trong graph |
| quiz_structure | Quiz có bốn options và đáp án nằm trong options; chưa xác nhận đáp án đúng về nghĩa |
| quiz_citations | Quiz có citation trỏ về chunk được kiểm tra; chưa xác nhận citation hỗ trợ đáp án |
| semantic_groundedness | Câu hỏi/đáp án được nội dung nguồn hỗ trợ về nghĩa; hiện BLOCKED |
| mastery | Cập nhật tỷ lệ đúng có trọng số: đúng weight 1 → 1.0; thêm sai weight 3 → 0.25 |
| weak_state | Mastery 0.25 được phân loại weak |
| recommendation_concept | Chọn đúng prerequisite expected hoặc review concept hiện tại |
| recommendation_source | Recommendation trả slide đúng expected |
| destination_api | API truy xuất được nội dung slide đích; không chứng minh điều hướng trên giao diện |
| browser_click | Click recommendation trên FE đến đúng nguồn; hiện chưa được thực thi |
| refusal_payload | Khi từ chối, options rỗng; theo runner đã trao đổi, chưa kiểm tra toàn bộ payload refusal |

## Chi tiết các kiểm tra FAIL

### case_01 — relationships

- Expected: `loss_function->gradient_descent:prerequisite_of`.
- Actual: `gradient_descent->loss_function:used_for`, `loss_function->gradient_descent:prerequisite_of`.
- Sai khác: có đủ cạnh expected nhưng thêm cạnh `used_for` ngược hướng so với cạnh prerequisite.
- Hướng xử lý: reviewer xác định cạnh dư có hợp lệ theo nội dung hay không; nếu golden chỉ quy định cạnh bắt buộc, cần quy tắc đánh giá cho phép cạnh bổ sung hợp lệ. Không xóa cạnh hoặc sửa golden chỉ để tăng điểm.

### case_09 — concepts

- Expected: `feature_vector`, `weight_vector`.
- Actual: `feature_vector`, `vector`, `weight_vector`.
- Sai khác: dư concept tổng quát `vector`.
- Hướng xử lý: kiểm tra matcher có nhận alias nằm trong cụm dài hay không; chốt chính sách giữ concept cha/con hoặc ưu tiên cụm cụ thể.

### case_10 — concepts

- Expected: `testing_data`, `training_data`.
- Actual: `ai`, `testing_data`, `training_data`.
- Sai khác: dư `ai`.
- Hướng xử lý: kiểm tra word boundary của alias ngắn `ai`; có khả năng khớp một phần từ khác, nhưng output hiện tại chưa đủ chứng minh nguyên nhân.

### case_13 — concepts

- Expected: `overfitting`.
- Actual: `ai`, `overfitting`, `training_data`.
- Sai khác: dư `ai` và `training_data`.
- Hướng xử lý: kiểm tra alias `ai` và reviewer xem training_data có thực sự được nhắc tới như concept cần trích xuất hay golden đang thiếu annotation.

### case_15 — quiz_decision

- Expected: `REFUSE_UNGROUNDED`.
- Actual: `GENERATE_QUIZ`.
- Sai khác: hệ thống sinh quiz khi expected yêu cầu từ chối.
- Hướng xử lý: kiểm tra nguồn có đủ bằng chứng hỗ trợ câu hỏi/đáp án không; source metadata tồn tại không đủ chứng minh groundedness.

### case_16 — concepts

- Expected: `linear_function`, `linear_regression`.
- Actual: `linear_function`, `linear_regression`, `regression`.
- Sai khác: dư concept tổng quát `regression`.
- Hướng xử lý: xử lý alias lồng nhau hoặc annotate rõ khi nào cần giữ cả linear_regression và regression.

### case_16 — relationships

- Expected: `linear_function->linear_regression:used_for`.
- Actual: `linear_regression->linear_function:used_for`.
- Sai khác: **đảo hướng cạnh**.
- Hướng xử lý: chốt định nghĩa source/target của used_for, kiểm tra rule extraction và đối chiếu câu nguồn.

### case_17 — quiz_decision

- Expected: `DISAMBIGUATE`.
- Actual: `GENERATE_QUIZ`.
- Sai khác: chưa yêu cầu làm rõ khi expected xác định nội dung nhập nhằng.
- Hướng xử lý: bổ sung điều kiện disambiguation và response làm rõ dựa trên case; không coi nhiều source luôn là nhập nhằng.

### case_20 — concepts

- Expected: `self_attention`, `transformer`.
- Actual: `layer`, `self_attention`, `transformer`.
- Sai khác: dư `layer`.
- Hướng xử lý: reviewer xác định layer có là concept độc lập trong câu nguồn không; thống nhất mức độ chi tiết của golden và extractor.

### case_21 — relationships

- Expected: `loss_function->gradient_descent:prerequisite_of`.
- Actual: `gradient_descent->loss_function:used_for`, `loss_function->gradient_descent:prerequisite_of`.
- Sai khác: thêm cạnh used_for ngoài expected, cùng dạng case_01.
- Hướng xử lý: kiểm tra bằng chứng của cạnh bổ sung và chính sách so sánh exact/subset.

### case_22 — concepts

- Expected: `softmax`.
- Actual: `ai`, `softmax`.
- Sai khác: dư `ai`.
- Hướng xử lý: kiểm tra alias ngắn theo boundary; xác nhận bằng input_chunk trước khi kết luận lỗi matching.

## Các case không có FAIL được liệt kê

Output cung cấp không liệt kê FAIL cho: `case_02`, `case_03`, `case_04`, `case_05`, `case_06`, `case_07`, `case_08`, `case_11`, `case_12`, `case_14`, `case_18`, `case_19`.

Đây là **12 case không có FAIL được liệt kê**, không phải 12 case E2E hoàn chỉnh: browser click còn BLOCKED và semantic groundedness chưa được chấm cho các case sinh quiz.

## Vì sao có metric chỉ đếm 21 hoặc 1 case?

Theo luồng runner đã trao đổi, 21 case thực tế trả GENERATE_QUIZ nên chạy các bước quiz/mastery/recommendation; một case trả refusal nên chạy refusal_payload. Output tổng hợp không cho biết ID của case refusal, nên báo cáo không suy đoán ID.

Case mong đợi refusal nhưng actual sinh quiz vẫn chạy kiểm tra structure/mastery; quiz_decision sẽ fail riêng. Do đó PASS về cấu trúc không phủ định lỗi quyết định sinh quiz.

Runner hiện thiếu bản ghi N/A ở nhánh không áp dụng. Cần ghi đầy đủ 22 bản ghi cho mỗi metric, phân biệt:

- **PASS:** thực thi và đạt điều kiện test.
- **FAIL:** thực thi nhưng khác expected.
- **BLOCKED:** chưa thể kiểm tra do thiếu capability/test.
- **ERROR:** lỗi thực thi.
- **N/A:** bước không áp dụng cho case.

Browser click hiện BLOCKED cả 22 theo báo cáo; case refusal không có recommendation để click có thể chuyển N/A nếu đó là định nghĩa chính thức của flow.

## Việc cần thực hiện tiếp

1. Review các concept dư và word boundary cho alias ngắn/cụm lồng nhau; đối chiếu input trước khi sửa expected.
2. Chốt hướng cạnh used_for và chính sách chấp nhận cạnh bổ sung có bằng chứng.
3. Hoàn thiện refusal/disambiguation dựa trên nội dung bằng chứng, không chỉ metadata.
4. Bổ sung semantic groundedness bằng expected answer/evidence hoặc reviewer độc lập.
5. Hoàn thiện nối AI output vào backend production và backend tự chấm đáp án nếu vẫn đang dùng adapter/client is_correct.
6. Thêm browser test click recommendation và xác nhận slide/video đích; API đích tồn tại chưa đủ.
7. Báo cáo N/A đầy đủ, tỷ lệ từng metric và trạng thái E2E theo từng case; không tính BLOCKED thành PASS.
