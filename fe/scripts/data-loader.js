/**
 * data-loader.js
 * -----------------------------------------------------------------------
 * Nguồn dữ liệu bài giảng cho toàn bộ app.
 *
 * Có 2 nguồn, tự chọn theo BACKEND_BASE_URL:
 *   - "" (rỗng)  -> dùng mock trong fe/data/lesson-mock.js
 *   - có giá trị -> gọi backend thật của Tài (route thật, đọc từ BE.md):
 *       GET {BASE}/lessons/{lesson_id}          -> title, video_url, duration_seconds, concepts[]
 *       GET {BASE}/knowledge-graph/{lesson_id}  -> { nodes: [{id,label,slide,start_time,end_time}],
 *                                                    edges: [{from,to,type}] }
 *       GET {BASE}/mastery/{student_id}         -> { mastery_summary: { <concept_id>: {name,score,state} } }
 *
 *   Backend KHÔNG có endpoint sinh quiz (chỉ có POST /quiz/answer để NỘP đáp
 *   án) — quiz_bank vẫn luôn lấy từ mock, dù đang nối backend thật hay không.
 *
 * Field name bên backend KHÁC mock (id/label/from/to thay vì
 * concept_id/name/source_concept_id/target_concept_id) — normalizeBackendData()
 * bên dưới lo việc chuyển đổi, phần còn lại của app không cần biết chuyện này.
 */

// Để rỗng "" = luôn dùng mock. Điền URL khi muốn nối backend thật đang chạy local.
const BACKEND_BASE_URL = "http://127.0.0.1:8000/adaptive";
const LESSON_ID = "lesson_01"; // bài "Machine Learning Core Concepts" — Tài đã có sẵn graph thật
const STUDENT_ID = "demo_student"; // cố định tạm cho demo, chưa có hệ thống tài khoản

async function loadLessonData() {
  if (BACKEND_BASE_URL) {
    try {
      const [lessonRes, graphRes, masteryRes] = await Promise.all([
        fetch(`${BACKEND_BASE_URL}/lessons/${LESSON_ID}`),
        fetch(`${BACKEND_BASE_URL}/knowledge-graph/${LESSON_ID}`),
        fetch(`${BACKEND_BASE_URL}/mastery/${STUDENT_ID}`)
      ]);
      if (!lessonRes.ok || !graphRes.ok) throw new Error("Backend trả lỗi");
      const lesson = await lessonRes.json();
      const graph = await graphRes.json();
      const mastery = masteryRes.ok ? await masteryRes.json() : null;
      return normalizeBackendData(lesson, graph, mastery);
    } catch (err) {
      console.warn("[data-loader] Gọi backend thật thất bại, dùng mock thay thế:", err.message);
    }
  }

  // Dùng biến JS nạp sẵn từ data/lesson-mock.js (script tag) — KHÔNG dùng fetch() ở đây vì
  // mở index.html trực tiếp qua "file://" bị trình duyệt chặn fetch() đọc file JSON local (CORS).
  if (!window.__LESSON_MOCK__) {
    throw new Error('Chưa nạp data/lesson-mock.js — kiểm tra thẻ <script> trong index.html');
  }
  return normalizeMockData(window.__LESSON_MOCK__);
}

/** Ghép 3 response thật của backend (lesson + graph + mastery) về đúng 1 hình dạng chung cho app dùng. */
function normalizeBackendData(lesson, graph, mastery) {
  const descriptionByConceptId = new Map((lesson.concepts || []).map(c => [c.concept_id, c.description]));
  const masterySummary = mastery?.mastery_summary || {};

  const nodes = (graph.nodes || []).map(n => {
    const m = masterySummary[n.id];
    return {
      concept_id: n.id,
      name: n.label,
      description: descriptionByConceptId.get(n.id) || "",
      formula: null, // backend chưa có field này
      slide: n.slide ?? null,
      start_time: n.start_time ?? null,
      end_time: n.end_time ?? null,
      mastery_score: m?.score ?? null,
      mastery_state: m?.state || "not_learned"
    };
  });

  const edges = (graph.edges || []).map(e => ({
    source_concept_id: e.from,
    target_concept_id: e.to,
    relation_type: e.type
  }));

  return {
    lessonId: lesson.lesson_id,
    title: lesson.title,
    durationSec: lesson.duration_seconds,
    videoUrl: lesson.video_url || null,
    nodes,
    edges,
    // Backend không sinh quiz -> luôn lấy quiz mẫu từ mock, kể cả khi graph là dữ liệu thật.
    quizBank: (window.__LESSON_MOCK__ && window.__LESSON_MOCK__.quiz_bank) || {}
  };
}

/** Chuẩn hoá dữ liệu mock (fe/data/lesson-mock.js) về cùng hình dạng trên. */
function normalizeMockData(raw) {
  return {
    lessonId: raw.lesson_id,
    title: raw.title,
    durationSec: raw.duration_sec,
    videoUrl: raw.video_url || null,
    nodes: raw.nodes || [],
    edges: raw.edges || [],
    quizBank: raw.quiz_bank || {}
  };
}
