/**
 * lesson-mock.js
 * -----------------------------------------------------------------------
 * Y HỆT nội dung "lesson-mock.json" trong cùng thư mục (giữ .json ở đó để
 * dễ đọc/đối chiếu với schema backend), nhưng đóng gói thành biến JS toàn
 * cục thay vì phải fetch() — vì mở file index.html trực tiếp bằng
 * "file://" (không qua server), trình duyệt (đặc biệt Chrome) CHẶN
 * fetch() đọc file JSON cục bộ do chính sách CORS. Nạp qua thẻ <script>
 * thường thì không bị chặn.
 *
 * Nếu sau này chạy qua 1 local server (vd `npx serve fe`, VSCode Live
 * Server) thì fetch() JSON sẽ hoạt động bình thường — data-loader.js vẫn
 * ưu tiên dùng biến này để không phải đổi gì cả.
 */
window.__LESSON_MOCK__ = {
  "lesson_id": "lesson_ml_intro",
  "title": "Nhập môn Machine Learning",
  "duration_sec": 900,
  "video_url": "https://www.youtube.com/watch?v=aircAruvnKk",
  "_comment_video_url_test": "Link YouTube TẠM (video 3Blue1Brown về Neural Network, chỉ để test embed) — thay bằng link video bài giảng thật của Tài khi có.",

  "nodes": [
    {
      "concept_id": "c1",
      "name": "Machine Learning",
      "description": "Hệ thống học các quy luật từ dữ liệu để đưa ra dự đoán cho dữ liệu mới chưa từng thấy.",
      "formula": "y = f(x; θ)",
      "slide": 1,
      "start_time": 0,
      "end_time": 180,
      "mastery_score": 0.92,
      "mastery_state": "mastered"
    },
    {
      "concept_id": "c2",
      "name": "Supervised Learning",
      "description": "Mô hình học từ tập dữ liệu có gán nhãn, phân nhánh thành Hồi quy (Regression) và Phân loại (Classification).",
      "formula": "D = {(x₁,y₁), ..., (xₙ,yₙ)}",
      "slide": 2,
      "start_time": 180,
      "end_time": 360,
      "mastery_score": 0.86,
      "mastery_state": "mastered"
    },
    {
      "concept_id": "c3",
      "name": "Regression",
      "description": "Mô hình ước lượng giá trị liên tục bằng cách tìm trọng số w và độ lệch b tối ưu.",
      "formula": "ŷ = w·x + b",
      "slide": 3,
      "start_time": 360,
      "end_time": 540,
      "mastery_score": 0.74,
      "mastery_state": "learning"
    },
    {
      "concept_id": "c4",
      "name": "Loss Function",
      "description": "Đo lường tổng bình phương sai số. Mục tiêu huấn luyện là cực tiểu hoá hàm J(w,b).",
      "formula": "J(w,b) = 1/2m · Σ(ŷ-y)²",
      "slide": 4,
      "start_time": 540,
      "end_time": 720,
      "mastery_score": 0.43,
      "mastery_state": "weak"
    },
    {
      "concept_id": "c5",
      "name": "Gradient Descent",
      "description": "Thuật toán tối ưu hoá lặp đi lặp lại để cập nhật w theo hướng giảm nhanh nhất của Loss Function.",
      "formula": "w := w - α·∇J(w)",
      "slide": 5,
      "start_time": 720,
      "end_time": 900,
      "mastery_score": 0.31,
      "mastery_state": "weak"
    },
    {
      "concept_id": "c6",
      "name": "Classification",
      "description": "Bài toán phân loại nhãn rời rạc — nhánh phụ, chưa học trong bài giảng này.",
      "formula": null,
      "slide": null,
      "start_time": null,
      "end_time": null,
      "mastery_score": null,
      "mastery_state": "not_learned"
    }
  ],

  "edges": [
    { "source_concept_id": "c1", "target_concept_id": "c2", "relation_type": "prerequisite" },
    { "source_concept_id": "c2", "target_concept_id": "c3", "relation_type": "prerequisite" },
    { "source_concept_id": "c2", "target_concept_id": "c6", "relation_type": "prerequisite" },
    { "source_concept_id": "c3", "target_concept_id": "c4", "relation_type": "prerequisite" },
    { "source_concept_id": "c4", "target_concept_id": "c5", "relation_type": "prerequisite" }
  ],

  "quiz_bank": {
    "c1": [
      {
        "quiz_id": "q_c1_1",
        "concept_id": "c1",
        "question": "Machine Learning khác gì so với lập trình if-else truyền thống?",
        "options": [
          "ML chạy nhanh hơn nên luôn được ưu tiên dùng",
          "ML tự học quy luật từ dữ liệu thay vì con người viết sẵn luật y = f(x)",
          "ML chỉ hoạt động khi không có dữ liệu",
          "ML và if-else về bản chất là một, chỉ khác tên gọi"
        ],
        "correct_option": 1,
        "difficulty": 0.3
      }
    ],
    "c2": [
      {
        "quiz_id": "q_c2_1",
        "concept_id": "c2",
        "question": "Trong Supervised Learning, tập dữ liệu D = {(x₁,y₁), ..., (xₙ,yₙ)} có đặc điểm gì?",
        "options": [
          "Không có nhãn (label) đi kèm dữ liệu",
          "Mỗi điểm dữ liệu x đều có nhãn y tương ứng để mô hình học theo",
          "Chỉ dùng được cho bài toán Regression, không dùng được cho Classification",
          "Dữ liệu luôn phải là số nguyên"
        ],
        "correct_option": 1,
        "difficulty": 0.35
      }
    ],
    "c3": [
      {
        "quiz_id": "q_c3_1",
        "concept_id": "c3",
        "question": "Trong hồi quy tuyến tính ŷ = w·x + b, mục tiêu của việc huấn luyện là gì?",
        "options": [
          "Tăng số lượng dữ liệu đầu vào",
          "Tìm w và b sao cho dự đoán ŷ gần với y thật nhất",
          "Giảm số chiều của x xuống 1",
          "Loại bỏ toàn bộ nhiễu khỏi dữ liệu"
        ],
        "correct_option": 1,
        "difficulty": 0.4
      }
    ],
    "c4": [
      {
        "quiz_id": "q_c4_1",
        "concept_id": "c4",
        "question": "Hàm Loss Function J(w,b) trong bài dùng để đo điều gì?",
        "options": [
          "Tốc độ chạy của thuật toán",
          "Số lượng tham số của mô hình",
          "Tổng bình phương sai số giữa dự đoán và giá trị thật",
          "Số lượng dữ liệu training"
        ],
        "correct_option": 2,
        "difficulty": 0.6
      }
    ],
    "c5": [
      {
        "quiz_id": "q_c5_1",
        "concept_id": "c5",
        "question": "Nếu đạo hàm của Loss Function theo trọng số bằng 0 (Gradient = 0), thuật toán Gradient Descent sẽ thế nào?",
        "options": [
          "Bước nhảy đạt cực đại và nhảy vọt khỏi hàm",
          "Trọng số dừng cập nhật vì đã đạt điểm cực trị (cực tiểu hoặc điểm yên ngựa)",
          "Learning rate tự động nhân đôi",
          "Mô hình tự động thêm dữ liệu mới"
        ],
        "correct_option": 1,
        "difficulty": 0.75
      }
    ]
  }
};
