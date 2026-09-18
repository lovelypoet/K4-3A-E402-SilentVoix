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
const LESSON_ID = "lesson_25"; // CHỈ là bài mặc định lần đầu vào trang (chưa từng dán link nào)
const STUDENT_ID = "demo_student"; // cố định tạm cho demo, chưa có hệ thống tài khoản
const LESSON_STORAGE_KEY = "lesson_studio_current_lesson_id";

/**
 * Bài học đang xem phải được GHI NHỚ, không được reset về LESSON_ID mặc định.
 * Trước đây app không nhớ gì: mỗi lần trang nạp lại (F5, hoặc Live Server tự
 * refresh khi file thay đổi) là quay về LESSON_ID — mà video của lesson mặc
 * định lại đúng là link cũ, nên nhìn y hệt "dán link mới xong nó tự nhảy về
 * link cũ", trong khi thật ra backend đã ingest đúng link mới rồi.
 */
function getInitialLessonId() {
  const fromHash = location.hash.replace(/^#/, "").trim();
  if (fromHash) return fromHash;
  try {
    const saved = localStorage.getItem(LESSON_STORAGE_KEY);
    if (saved) return saved;
  } catch (err) {
    // localStorage bị chặn (chế độ ẩn danh...) -> bỏ qua, dùng mặc định
  }
  return LESSON_ID;
}

/** Gọi sau khi dán link mới thành công -> reload trang vẫn giữ nguyên bài vừa phân tích. */
function rememberLessonId(lessonId) {
  try {
    localStorage.setItem(LESSON_STORAGE_KEY, lessonId);
  } catch (err) {
    // như trên
  }
  location.hash = lessonId; // đổi hash KHÔNG nạp lại trang, chỉ để copy/chia sẻ được đúng bài
}

/**
 * Quên hẳn bài đã nhớ. Phải xoá CẢ hash trên URL, không chỉ localStorage: hash
 * được ưu tiên hơn localStorage trong getInitialLessonId(), nên nếu chỉ xoá
 * localStorage thì lần nạp trang sau vẫn đọc lại đúng id đã chết từ hash.
 */
function forgetLessonId() {
  try {
    localStorage.removeItem(LESSON_STORAGE_KEY);
  } catch (err) {
    // như trên
  }
  if (location.hash) {
    // replaceState thay vì gán location.hash="" để không để lại dấu "#" thừa
    // và không thêm một mục mới vào lịch sử trình duyệt.
    history.replaceState(null, "", location.pathname + location.search);
  }
}

/**
 * allowMockFallback=true (mặc định): lỗi thì âm thầm rơi về mock — hợp cho lúc
 * mở trang lần đầu (backend có thể chưa bật, vẫn muốn xem được giao diện).
 * allowMockFallback=false: NÉM LỖI THẬT ra ngoài, không rơi về mock — bắt buộc
 * dùng khi load 1 lesson_id CỤ THỂ vừa ingest xong (VD sau khi dán link video
 * mới) — vì nếu lặng lẽ rơi về mock lúc này, người dùng sẽ thấy y hệt data mock
 * cũ và tưởng nhầm là "link mới không ăn", trong khi thực ra có lỗi thật đang
 * bị nuốt mất không ai biết.
 */
async function loadLessonData(lessonId = LESSON_ID, { allowMockFallback = true } = {}) {
  if (BACKEND_BASE_URL) {
    try {
      const [lessonRes, graphRes, masteryRes] = await Promise.all([
        fetch(`${BACKEND_BASE_URL}/lessons/${lessonId}`),
        fetch(`${BACKEND_BASE_URL}/knowledge-graph/${lessonId}`),
        fetch(`${BACKEND_BASE_URL}/mastery/${STUDENT_ID}`)
      ]);
      // Gắn kèm .status để nơi gọi phân biệt được "bài học không còn tồn tại" (404)
      // với "backend chưa bật" (lỗi mạng, không có status) — hai tình huống cần
      // xử lý khác hẳn nhau, xem chỗ khởi động trong app.js.
      if (!lessonRes.ok) throw Object.assign(new Error(`GET /lessons/${lessonId} lỗi ${lessonRes.status}`), { status: lessonRes.status });
      if (!graphRes.ok) throw Object.assign(new Error(`GET /knowledge-graph/${lessonId} lỗi ${graphRes.status}`), { status: graphRes.status });
      const lesson = await lessonRes.json();
      const graph = await graphRes.json();
      const mastery = masteryRes.ok ? await masteryRes.json() : null;
      return normalizeBackendData(lesson, graph, mastery);
    } catch (err) {
      if (!allowMockFallback) throw err; // để lỗi lộ ra ngoài cho loadVideoFromInput() bắt và alert
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

/**
 * Lấy lesson_id từ response ingest của backend.
 *
 * api.py có cơ chế chống trùng nguồn: mỗi video YouTube / mỗi file được gắn
 * `source_key`; nếu nguồn đó đã ingest rồi thì backend KHÔNG tạo bài mới nữa
 * mà trả về {status: "DUPLICATE_SOURCE", existing_lesson_id: "..."} — không có
 * field `lesson`. Đây là hành vi cố ý, không phải lỗi: dán lại đúng link cũ thì
 * ta mở lại bài đã phân tích sẵn (nhanh hơn, khỏi phân tích lại từ đầu).
 *
 * Hiện backend trả dạng này kèm HTTP 200; phòng khi sau này đổi sang 409 (mã
 * chuẩn cho "đã tồn tại") thì hàm này vẫn đọc được cả hai.
 */
async function readIngestedLessonId(res, kind) {
  if (!res.ok && res.status !== 409) {
    throw new Error(`Ingest ${kind} thất bại (${res.status})`);
  }
  const data = await res.json().catch(() => ({}));
  const lessonId = data?.lesson?.lesson_id || data?.existing_lesson_id;
  if (!lessonId) {
    throw new Error(data?.message || data?.detail || `Backend không trả về lesson_id sau khi ingest ${kind}.`);
  }
  return lessonId;
}

/**
 * Luồng THẬT, đầu-cuối: đưa 1 link video vào → backend ingest (trích transcript
 * thật nếu là YouTube) → AI (ai.pipeline) đọc transcript đó sinh graph MỚI, ghi
 * đè vào lesson vừa tạo → trả về lesson_id mới để load lại toàn bộ app theo data
 * NÀY (khác hẳn createVideoPlayer() cũ chỉ đổi video, không đụng gì đến Graph).
 *
 * Link không phải YouTube (không có transcript) hoặc nội dung không khớp từ
 * khoá nào trong ai/ -> graph rỗng, ĐÚNG kỳ vọng (không có gì để suy ra thì
 * không tự bịa ra khái niệm), không phải lỗi.
 */
async function ingestVideoAndGenerateGraph(videoUrl) {
  if (!BACKEND_BASE_URL) {
    throw new Error("Chưa bật BACKEND_BASE_URL — không thể gọi AI phân tích thật.");
  }

  const ingestRes = await fetch(`${BACKEND_BASE_URL}/lessons/video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_url: videoUrl })
  });
  const newLessonId = await readIngestedLessonId(ingestRes, "video");

  const generateRes = await fetch(`${BACKEND_BASE_URL}/lessons/${newLessonId}/generate-graph`, {
    method: "POST"
  });
  if (!generateRes.ok) {
    const errBody = await generateRes.json().catch(() => ({}));
    throw new Error(errBody.detail || `Sinh graph thất bại (${generateRes.status})`);
  }

  return newLessonId;
}

/**
 * Y hệt ingestVideoAndGenerateGraph() nhưng cho nguồn PDF slide — backend đã
 * có sẵn cả 2 endpoint (POST /lessons/slide + /generate-graph) từ trước, chỉ
 * là ô "Dán link PDF" ở giao diện chưa từng gọi tới (trước giờ chỉ nhúng
 * <iframe> xem trước, không phân tích AI). Đã kiểm bằng curl: backend đọc PDF
 * thật, tách được chunk theo từng trang, `ai/` build_graph vẫn chạy ra khái
 * niệm + cạnh y như với transcript video.
 */
async function ingestSlideAndGenerateGraph(slideUrl) {
  if (!BACKEND_BASE_URL) {
    throw new Error("Chưa bật BACKEND_BASE_URL — không thể gọi AI phân tích thật.");
  }

  const ingestRes = await fetch(`${BACKEND_BASE_URL}/lessons/slide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ slide_url: slideUrl })
  });
  const newLessonId = await readIngestedLessonId(ingestRes, "slide");

  const generateRes = await fetch(`${BACKEND_BASE_URL}/lessons/${newLessonId}/generate-graph`, {
    method: "POST"
  });
  if (!generateRes.ok) {
    const errBody = await generateRes.json().catch(() => ({}));
    throw new Error(errBody.detail || `Sinh graph thất bại (${generateRes.status})`);
  }

  return newLessonId;
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

  const filteredNodes = filterRawSlideNodes(lesson.lesson_id, nodes);
  const merged = mergeDuplicateConcepts(lesson.lesson_id, filteredNodes, edges);
  const transcript = lesson.transcript || [];

  return {
    isMock: false,
    lessonId: lesson.lesson_id,
    title: lesson.title,
    durationSec: lesson.duration_seconds,
    videoUrl: lesson.video_url || null,
    transcript,
    nodes: attachTranscriptEvidence(merged.nodes, transcript),
    edges: merged.edges,
    // Backend không sinh quiz -> luôn lấy quiz mẫu từ mock, kể cả khi graph là dữ liệu thật.
    quizBank: (window.__LESSON_MOCK__ && window.__LESSON_MOCK__.quiz_bank) || {}
  };
}

/**
 * Chuẩn hoá dữ liệu mock (fe/data/lesson-mock.js) về cùng hình dạng trên.
 * isMock=true để app.js BÁO RÕ RA MÀN HÌNH rằng đây là dữ liệu mẫu — trước đây
 * việc rơi về mock diễn ra âm thầm (chỉ console.warn), khiến người dùng tưởng
 * đang xem dữ liệu thật từ backend và mất rất nhiều thời gian truy sai hướng.
 */
function normalizeMockData(raw) {
  return {
    isMock: true,
    lessonId: raw.lesson_id,
    title: raw.title,
    durationSec: raw.duration_sec,
    videoUrl: raw.video_url || null,
    transcript: raw.transcript || [],
    nodes: raw.nodes || [],
    edges: raw.edges || [],
    quizBank: raw.quiz_bank || {}
  };
}

/**
 * Với lesson nguồn PDF/slide, bộ tự trích xuất của Tài (ingestion.py) không lọc
 * theo từ khoá như với video — nó tạo THẲNG 1 node CHO MỖI TRANG, lấy nguyên
 * dòng đầu tiên của trang làm tên (id dạng "c_{lesson_id}_slide_{số trang}"),
 * kể cả khi dòng đó chỉ là tiêu đề phụ/câu dở dang, không phải khái niệm thật.
 * PDF nhiều trang -> hàng chục "node" kiểu này chồng lên đúng vài node thật do
 * ai/ sinh ra, làm graph rối không đọc nổi. Các node này KHÔNG BAO GIỜ có cạnh
 * (ingestion.py không sinh quan hệ), nên lọc bỏ ở đây không mất liên kết nào,
 * chỉ bớt nhiễu hiển thị — dữ liệu gốc trong backend vẫn giữ nguyên.
 */
function filterRawSlideNodes(lessonId, nodes) {
  const rawSlidePattern = new RegExp(`^c_${escapeRegExp(lessonId)}_slide_\\d+$`);
  return nodes.filter(n => !rawSlidePattern.test(n.concept_id));
}

/**
 * Backend hiện có 2 bộ trích xuất khái niệm chạy song song trên cùng 1 lesson
 * (ingestion.py của Tài: id dạng "c_{lesson_id}_{từ khoá}", KHÔNG BAO GIỜ sinh
 * cạnh; ai/pipeline của Anh: id dạng "ai_{lesson_id}_{từ khoá}", CÓ sinh cạnh
 * nhưng chỉ cho 8 cặp từ khoá cố định). Khi cả 2 hệ cùng bắt được 1 khái niệm
 * (ví dụ "gradient descent"), kết quả là 2 NODE RIÊNG cho cùng 1 thứ — một node
 * có cạnh (của Anh) và một node mồ côi (của Tài), làm graph vừa rối vừa ít cạnh
 * hơn thực tế.
 *
 * Vì 2 hệ ID đều đặt tên theo CÙNG một từ khoá gốc (chỉ khác tiền tố), phần đuôi
 * sau khi bỏ tiền tố CHÍNH LÀ chìa khoá để nhận ra 2 node là 1 khái niệm — đây
 * là so khớp chính xác dựa trên dữ liệu có thật, không phải đoán mò hay suy diễn
 * quan hệ mới. Gộp xong: giữ lại node có cạnh (nếu có) làm id sống sót, nối lại
 * mọi cạnh trỏ tới node bị gộp, và ghép tên/mô tả để không mất thông tin.
 */
function mergeDuplicateConcepts(lessonId, nodes, edges) {
  const stripPrefix = new RegExp(`^(ai_|c_)${escapeRegExp(lessonId)}_`);
  const keyOf = node => {
    const stripped = node.concept_id.replace(stripPrefix, "");
    return stripped !== node.concept_id ? stripped : node.concept_id; // không khớp mẫu -> coi là khái niệm riêng, không gộp nhầm
  };

  const groups = new Map();
  nodes.forEach(n => {
    const key = keyOf(n);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(n);
  });

  const idRemap = new Map(); // id cũ -> id sống sót sau gộp
  const mergedNodes = [];

  groups.forEach(group => {
    if (group.length === 1) {
      mergedNodes.push(group[0]);
      return;
    }
    // Ưu tiên node của Anh (ai_...) làm id sống sót vì chỉ hệ này mới có cạnh.
    const primary = group.find(n => n.concept_id.startsWith("ai_")) || group[0];
    group.forEach(n => idRemap.set(n.concept_id, primary.concept_id));

    const names = [...new Set(group.map(n => n.name).filter(Boolean))];
    const hasVietnamese = s => /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i.test(s);
    const displayName = names.find(hasVietnamese) || names.sort((a, b) => b.length - a.length)[0];
    const otherNames = names.filter(n => n !== displayName && !displayName.includes(n));

    const descriptions = [...new Set(group.map(n => n.description).filter(Boolean))];

    mergedNodes.push({
      ...primary,
      name: otherNames.length ? `${displayName} (${otherNames.join(", ")})` : displayName,
      description: descriptions.join(" ") || primary.description,
      start_time: minOrNull(group.map(n => n.start_time)),
      end_time: maxOrNull(group.map(n => n.end_time)),
      slide: group.map(n => n.slide).find(s => s != null) ?? null,
      mastery_score: group.map(n => n.mastery_score).find(s => s != null) ?? null,
      mastery_state: group.map(n => n.mastery_state).find(s => s && s !== "not_learned") || primary.mastery_state
    });
  });

  const remapId = id => idRemap.get(id) || id;
  const seenEdge = new Set();
  const mergedEdges = [];
  edges.forEach(e => {
    const source = remapId(e.source_concept_id);
    const target = remapId(e.target_concept_id);
    if (source === target) return; // 2 node gộp làm 1 -> cạnh giữa chúng biến mất, đúng bản chất
    const key = `${source}->${target}`;
    if (seenEdge.has(key)) return;
    seenEdge.add(key);
    mergedEdges.push({ ...e, source_concept_id: source, target_concept_id: target });
  });

  return { nodes: mergedNodes, edges: mergedEdges };
}

function minOrNull(values) {
  const nums = values.filter(v => v != null);
  return nums.length ? Math.min(...nums) : null;
}
function maxOrNull(values) {
  const nums = values.filter(v => v != null);
  return nums.length ? Math.max(...nums) : null;
}
function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Mô tả của backend chỉ là 1 câu viết sẵn theo từ khoá (không đọc transcript).
 * Bù lại bằng cách tìm trong CHÍNH transcript thật những đoạn có nhắc tới khái
 * niệm này (so khớp cụm từ, không suy diễn) để làm bằng chứng cụ thể, kèm mốc
 * giây thật — bấm vào là tua video tới đúng chỗ đó.
 */
function attachTranscriptEvidence(nodes, transcript) {
  if (!transcript || !transcript.length) return nodes;

  return nodes.map(node => {
    const phrases = buildSearchPhrases(node);
    const matches = [];
    for (const chunk of transcript) {
      const text = (chunk.text || "").toLowerCase();
      if (phrases.some(p => text.includes(p))) {
        matches.push({ start_time: chunk.start_time, text: (chunk.text || "").trim() });
      }
    }
    matches.sort((a, b) => (a.start_time ?? 0) - (b.start_time ?? 0));
    return { ...node, evidence: matches.slice(0, 3) };
  });
}

function buildSearchPhrases(node) {
  const raw = [node.name, node.concept_id.replace(/^(ai_|c_)[^_]+_[^_]+_/, "").replace(/_/g, " ")];
  const phrases = new Set();
  raw.forEach(s => {
    if (!s) return;
    // Bỏ phần trong ngoặc (thường là tên gộp thêm) và dấu câu, chỉ giữ cụm từ chính.
    const cleaned = s.replace(/\([^)]*\)/g, "").replace(/[^\p{L}\p{N}\s]/gu, "").trim().toLowerCase();
    if (cleaned.length >= 4) phrases.add(cleaned);
  });
  return [...phrases];
}
