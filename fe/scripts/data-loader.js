/**
 * data-loader.js
 * -----------------------------------------------------------------------
 * Nguồn dữ liệu bài giảng cho toàn bộ app.
 *
 * HIỆN TẠI: đọc từ file mock "fe/data/lesson-mock.json" (do Long tự dựng để
 * dev UI, không cần chờ backend của Tài).
 *
 * SAU NÀY KHI NỐI BACKEND THẬT: chỉ cần sửa BACKEND_BASE_URL bên dưới thành
 * URL thật (ví dụ "http://127.0.0.1:8000" hoặc URL Vercel serverless), API
 * đã được thiết kế khớp sẵn theo đúng response của Tài:
 *   GET {BACKEND_BASE_URL}/knowledge-graph/{lesson_id}  -> { nodes, edges }
 *   GET {BACKEND_BASE_URL}/lessons/{lesson_id}          -> thông tin bài học
 * loadLessonData() sẽ tự ưu tiên gọi backend thật nếu BACKEND_BASE_URL khác
 * rỗng, lỗi/không có backend thì tự rơi về mock — code gọi chỗ khác không
 * cần sửa gì thêm.
 */

// Để rỗng "" = luôn dùng mock. Điền URL vào đây khi Tài deploy xong backend.
const BACKEND_BASE_URL = "";
const LESSON_ID = "lesson_ml_intro";

async function loadLessonData() {
  if (BACKEND_BASE_URL) {
    try {
      const [lessonRes, graphRes] = await Promise.all([
        fetch(`${BACKEND_BASE_URL}/lessons/${LESSON_ID}`),
        fetch(`${BACKEND_BASE_URL}/knowledge-graph/${LESSON_ID}`)
      ]);
      if (!lessonRes.ok || !graphRes.ok) throw new Error("Backend trả lỗi");
      const lesson = await lessonRes.json();
      const graph = await graphRes.json();
      return normalizeLessonData({ ...lesson, nodes: graph.nodes, edges: graph.edges });
    } catch (err) {
      console.warn("[data-loader] Gọi backend thật thất bại, dùng mock thay thế:", err.message);
    }
  }

  // Dùng biến JS nạp sẵn từ data/lesson-mock.js (script tag) — KHÔNG dùng fetch() ở đây vì
  // mở index.html trực tiếp qua "file://" bị trình duyệt chặn fetch() đọc file JSON local (CORS).
  // Nội dung y hệt data/lesson-mock.json (giữ file .json đó lại để đối chiếu schema với backend).
  if (!window.__LESSON_MOCK__) {
    throw new Error('Chưa nạp data/lesson-mock.js — kiểm tra thẻ <script> trong index.html');
  }
  return normalizeLessonData(window.__LESSON_MOCK__);
}

/** Chuẩn hoá dữ liệu về đúng 1 hình dạng chung, dù nguồn là mock hay backend thật. */
function normalizeLessonData(raw) {
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
