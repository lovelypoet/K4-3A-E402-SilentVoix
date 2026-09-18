/**
 * app.js — điểm khởi động, nối các module lại với nhau.
 * data-loader.js / graph.js / video-player.js / quiz.js đều là hàm thuần,
 * không tự chạy — app.js chịu trách nhiệm wiring toàn bộ luồng:
 *
 *   video timeupdate  ──► graph.setActiveConcept + revealUpTo + panel chi tiết
 *   click node graph  ──► hiện popup "Chi tiết khái niệm" ngay trong panel Graph
 *                         (KHÔNG tua video — node vẽ nhỏ, bấm vào mới xem hết nội dung)
 *   mở quiz           ──► quiz.open(concept đang active)
 *   nộp quiz đúng     ──► cập nhật mastery trên graph + tính lại gợi ý ôn tập
 *   dán link video mới ──► ingestVideoAndGenerateGraph() (data-loader.js): BE
 *                          ingest thật + AI phân tích thật ra graph MỚI, rồi
 *                          bootLesson() load lại TOÀN BỘ app theo lesson đó —
 *                          Graph không còn cố định 1 lesson nữa.
 */

(async function main() {
  const els = {
    lessonTitle: document.getElementById("lesson-title"),
    videoContainer: document.getElementById("video-container"),
    graphSvg: document.getElementById("graph-svg"),
    conceptName: document.getElementById("concept-name"),
    conceptDesc: document.getElementById("concept-desc"),
    conceptFormula: document.getElementById("concept-formula"),
    conceptMastery: document.getElementById("concept-mastery"),
    btnOpenQuiz: document.getElementById("btn-open-quiz"),
    recommendationBox: document.getElementById("recommendation-box"),
    quizModal: document.getElementById("quiz-modal"),
    nodeDetailCard: document.getElementById("node-detail-card"),
    nodeDetailName: document.getElementById("node-detail-name"),
    nodeDetailFormula: document.getElementById("node-detail-formula"),
    nodeDetailDesc: document.getElementById("node-detail-desc"),
    nodeDetailSource: document.getElementById("node-detail-source"),
    nodeDetailMastery: document.getElementById("node-detail-mastery"),
    nodeDetailClose: document.getElementById("node-detail-close"),
    nodeDetailEvidenceBlock: document.getElementById("node-detail-evidence-block"),
    nodeDetailEvidence: document.getElementById("node-detail-evidence"),
    nodeDetailLinksBlock: document.getElementById("node-detail-links-block"),
    nodeDetailLinks: document.getElementById("node-detail-links"),
    videoLinkInput: document.getElementById("video-link-input"),
    videoLinkLoad: document.getElementById("video-link-load"),
    tabBtnVideo: document.getElementById("tab-btn-video"),
    tabBtnSlide: document.getElementById("tab-btn-slide"),
    slideView: document.getElementById("slide-view"),
    slideGenerated: document.getElementById("slide-generated"),
    slidePageBadge: document.getElementById("slide-page-badge"),
    slideTitle: document.getElementById("slide-title"),
    slideFormula: document.getElementById("slide-formula"),
    slideDesc: document.getElementById("slide-desc"),
    slideLinkInput: document.getElementById("slide-link-input"),
    slideLinkLoad: document.getElementById("slide-link-load"),
    slideLinkClear: document.getElementById("slide-link-clear"),
    slidePdfFrame: document.getElementById("slide-pdf-frame")
  };

  // State thay đổi mỗi lần nạp 1 lesson khác — "let" chứ không "const".
  let data, nodeById, graph, player;

  // quiz_bank hiện luôn lấy từ mock (BE chưa có endpoint sinh quiz) nên không
  // đổi theo lesson -> tạo modal quiz đúng 1 lần duy nhất, không tạo lại mỗi
  // lần đổi lesson (tạo lại sẽ gắn listener trùng lặp lên cùng 1 nút bấm).
  const quiz = createQuizController({
    modalEl: els.quizModal,
    quizBank: (window.__LESSON_MOCK__ && window.__LESSON_MOCK__.quiz_bank) || {},
    onAnswered: handleQuizAnswered
  });

  /**
   * Nạp và dựng lại TOÀN BỘ giao diện theo đúng 1 lesson_id — dùng cả lúc khởi
   * động trang lẫn lúc người dùng dán link video mới (sau khi AI phân tích
   * xong). Gọi lại hàm này là graph/video/panel chi tiết đều đổi theo lesson
   * mới hoàn toàn, không còn gì của lesson cũ sót lại.
   *
   * Node/edge hiển thị LUÔN LÀ đúng những gì backend trả về (GET
   * /knowledge-graph/{lesson_id}) — tức đúng kết quả của module ai/ (Đức Anh)
   * chạy trên dữ liệu ingest của Tài. Frontend không tự gọi AI riêng.
   */
  async function bootLesson(lessonId, { allowMockFallback = true } = {}) {
    data = await loadLessonData(lessonId, { allowMockFallback });
    // Hiện luôn lesson_id đang xem: trước đây không nhìn được app đang ở bài nào,
    // nên lúc bị reset về bài mặc định rất khó phát hiện. Và nếu đang chạy bằng
    // dữ liệu mẫu (backend chưa bật / lesson_id không tồn tại) thì phải nói
    // thẳng ra, đừng để người dùng tưởng nhầm là dữ liệu thật.
    els.lessonTitle.textContent = data.isMock
      ? `${data.title} · ⚠️ DỮ LIỆU MẪU (backend chưa chạy hoặc không có bài học này)`
      : data.lessonId
      ? `${data.title} · ${data.lessonId}`
      : data.title;
    els.lessonTitle.classList.toggle("lesson-title--mock", !!data.isMock);
    nodeById = new Map(data.nodes.map(n => [n.concept_id, n]));

    graph = renderGraph(els.graphSvg, data.nodes, data.edges);
    graph.onNodeClick(conceptId => {
      const node = nodeById.get(conceptId);
      if (node) renderNodeDetailCard(node); // chỉ hiện chi tiết, KHÔNG tua video
    });
    els.nodeDetailCard.hidden = true;

    if (player) player.destroy(); // tắt hẳn player lesson cũ — không thì 2 player chạy song song, gây nháy nội dung
    player = createVideoPlayer({
      container: els.videoContainer,
      durationSec: data.durationSec,
      videoUrl: data.videoUrl,
      onTimeUpdate: handleTimeUpdate
    });
    els.videoLinkInput.value = data.videoUrl || "";

    handleTimeUpdate(0);
  }

  // Ưu tiên bài đã xem gần nhất (hash trên URL / localStorage), KHÔNG mặc định
  // nhảy về LESSON_ID — nếu không, F5 (hoặc Live Server tự refresh) là mất bài
  // vừa dán link phân tích xong.
  //
  // Bài đã nhớ phải nạp với allowMockFallback:false. Nếu để mặc định (true), lúc
  // bài đó không còn tồn tại nữa thì loadLessonData âm thầm trả về mock và coi
  // như THÀNH CÔNG -> nhánh catch không bao giờ chạy -> id đã chết nằm lì trong
  // localStorage, mỗi lần mở trang lại gọi 404 rồi hiện mock mãi mãi.
  try {
    await bootLesson(getInitialLessonId(), { allowMockFallback: false });
  } catch (err) {
    // 404 = bài đã nhớ không còn (backend đổi storage, lesson bị xoá) -> quên hẳn đi.
    // Lỗi khác (backend chưa bật) -> GIỮ id lại, để lúc bật backend lên còn vào đúng bài cũ.
    if (err.status === 404) forgetLessonId();
    try {
      await bootLesson();
    } catch (err2) {
      els.videoContainer.innerHTML = `<div class="load-error">Không tải được dữ liệu bài học: ${err2.message}</div>`;
      return;
    }
  }

  /**
   * Dán link video mới -> gọi THẬT: backend ingest (trích transcript nếu là
   * YouTube) -> AI (ai.pipeline) đọc transcript đó sinh graph MỚI -> load lại
   * toàn bộ app theo đúng lesson vừa tạo. Video khác chủ đề (VD Java) sẽ ra
   * graph khác hẳn hoặc RỖNG (không có từ khoá nào khớp) — đúng bản chất, AI
   * không tự bịa khái niệm khi không có căn cứ.
   */
  async function loadVideoFromInput() {
    const url = els.videoLinkInput.value.trim();
    if (!url) return;

    const originalLabel = els.videoLinkLoad.textContent;
    els.videoLinkLoad.disabled = true;
    els.videoLinkLoad.textContent = "Đang phân tích bằng AI...";
    els.videoLinkInput.disabled = true;

    try {
      const newLessonId = await ingestVideoAndGenerateGraph(url);
      await bootLesson(newLessonId, { allowMockFallback: false }); // lỗi phải hiện alert thật, không âm thầm rơi về mock
      rememberLessonId(newLessonId); // reload trang vẫn ở đúng bài vừa phân tích, không bật về bài mặc định
    } catch (err) {
      alert("Không phân tích được video này: " + err.message);
    } finally {
      els.videoLinkLoad.disabled = false;
      els.videoLinkLoad.textContent = originalLabel;
      els.videoLinkInput.disabled = false;
    }
  }
  els.videoLinkLoad.addEventListener("click", loadVideoFromInput);
  els.videoLinkInput.addEventListener("keydown", (evt) => {
    if (evt.key === "Enter") loadVideoFromInput();
  });

  els.nodeDetailClose.addEventListener("click", () => {
    els.nodeDetailCard.hidden = true;
  });

  /**
   * Toggle Video / Slide — CÙNG 1 timeline (video vẫn chạy nền theo giây thật),
   * chỉ đổi cách hiển thị nội dung. Chuyển sang Slide thì tạm dừng video (đỡ
   * vừa xem slide vừa nghe tiếng chạy nền gây rối); quay lại Video thì thôi,
   * không tự play lại — để học viên chủ động bấm Play.
   */
  function switchTab(tab) {
    const showVideo = tab === "video";
    els.tabBtnVideo.classList.toggle("active", showVideo);
    els.tabBtnSlide.classList.toggle("active", !showVideo);
    els.videoContainer.hidden = !showVideo;
    els.slideView.hidden = showVideo;
    if (!showVideo) player.pause();
  }
  els.tabBtnVideo.addEventListener("click", () => switchTab("video"));
  els.tabBtnSlide.addEventListener("click", () => switchTab("slide"));

  /**
   * Dán link PDF slide -> NHÚNG XEM NGAY (iframe, không cần chờ) đồng thời gọi
   * THẬT: backend ingest PDF (tách theo từng trang) -> AI (ai.pipeline) đọc
   * nội dung đó sinh graph MỚI -> load lại toàn bộ app theo lesson vừa tạo.
   * Y hệt luồng dán link video, chỉ khác nguồn — trước đây ô này chỉ nhúng
   * xem trước, chưa từng gọi AI (đã kiểm bằng curl: backend + ai/ đọc PDF thật
   * ra đúng khái niệm/cạnh y như transcript video). Một số PDF chặn nhúng
   * iframe (X-Frame-Options) thì phần xem trước hiện trắng, nhưng việc phân
   * tích AI vẫn chạy bình thường vì đó là request riêng từ backend, không qua
   * iframe của trình duyệt.
   */
  async function loadSlidePdf() {
    const url = els.slideLinkInput.value.trim();
    if (!url) return;

    els.slidePdfFrame.src = url;
    els.slidePdfFrame.hidden = false;
    els.slideGenerated.hidden = true;
    els.slideLinkClear.hidden = false;

    const originalLabel = els.slideLinkLoad.textContent;
    els.slideLinkLoad.disabled = true;
    els.slideLinkLoad.textContent = "Đang phân tích bằng AI...";
    els.slideLinkInput.disabled = true;
    try {
      const newLessonId = await ingestSlideAndGenerateGraph(url);
      await bootLesson(newLessonId, { allowMockFallback: false });
      rememberLessonId(newLessonId);
      switchTab("slide"); // bootLesson() mặc định mở tab Video -> quay lại đúng tab đang thao tác
    } catch (err) {
      alert("Không phân tích được slide này: " + err.message);
    } finally {
      els.slideLinkLoad.disabled = false;
      els.slideLinkLoad.textContent = originalLabel;
      els.slideLinkInput.disabled = false;
    }
  }
  function clearSlidePdf() {
    els.slidePdfFrame.hidden = true;
    els.slidePdfFrame.src = "";
    els.slideGenerated.hidden = false;
    els.slideLinkClear.hidden = true;
  }
  els.slideLinkLoad.addEventListener("click", loadSlidePdf);
  els.slideLinkInput.addEventListener("keydown", (evt) => {
    if (evt.key === "Enter") loadSlidePdf();
  });
  els.slideLinkClear.addEventListener("click", clearSlidePdf);

  els.btnOpenQuiz.addEventListener("click", () => {
    const activeId = graph.getActiveConcept();
    const concept = nodeById.get(activeId);
    if (concept) quiz.open(concept);
  });

  // ---------------------------------------------------------------------

  function findConceptAtTime(sec) {
    return data.nodes.find(n => n.start_time != null && sec >= n.start_time && sec < n.end_time) || data.nodes[0];
  }

  function handleTimeUpdate(sec) {
    graph.revealUpTo(sec); // graph "mọc" dần theo đúng đoạn video đã xem tới
    const concept = findConceptAtTime(sec);
    // Lesson vừa ingest có thể chưa có khái niệm nào (bộ trích xuất của backend
    // không khớp từ khoá nào trong video này) — không được để văng lỗi ở đây.
    if (!concept) {
      graph.setActiveConcept(null);
      els.conceptName.textContent = "Chưa có khái niệm nào";
      els.conceptDesc.textContent = "Video này chưa khớp từ khoá nào trong bộ trích xuất khái niệm.";
      els.conceptFormula.hidden = true;
      els.conceptMastery.hidden = true;
      els.btnOpenQuiz.disabled = true;
      els.recommendationBox.hidden = true;
      return;
    }
    graph.setActiveConcept(concept.concept_id);
    renderConceptDetail(concept);
    renderSlideView(concept); // cùng dữ liệu, phòng khi đang ở tab Slide thì nội dung vẫn theo kịp đúng khái niệm
    renderRecommendation(concept);
    updateQuizButtonState(concept); // mỗi khái niệm tự có trạng thái nút riêng, không dùng chung 1 cờ toàn cục
  }

  /** Nội dung tab Slide — CÙNG dữ liệu concept, chỉ khác cách trình bày (dạng slide trình chiếu). */
  function renderSlideView(concept) {
    els.slidePageBadge.textContent = concept.slide != null ? `Slide ${concept.slide}` : "Chưa có slide";
    els.slideTitle.textContent = concept.name;
    els.slideFormula.textContent = concept.formula || "";
    els.slideFormula.hidden = !concept.formula;
    els.slideDesc.textContent = concept.description || "";
  }

  /**
   * Khái niệm đang active đã đạt 100% (đã "xong") -> disable nút Làm Quiz cho ĐÚNG
   * khái niệm đó. Video chạy sang khái niệm khác (chưa đạt 100%) thì hàm này được
   * gọi lại (từ handleTimeUpdate) với concept mới -> nút tự hiện lại bình thường.
   *
   * quiz_bank hiện chỉ có sẵn cho 5 khái niệm mock (c1-c5) — khái niệm lấy từ
   * backend thật CHƯA có câu hỏi nào khớp id, nên % không thể tăng được (không
   * phải lỗi hiển thị, mà là chưa có endpoint sinh quiz/lưu mastery ở backend —
   * xem phân công việc.md). Disable nút + nói rõ lý do thay vì để bấm vào rồi
   * không thấy gì xảy ra.
   */
  function updateQuizButtonState(concept) {
    const isDone = concept.mastery_score != null && concept.mastery_score >= 1;
    const hasQuiz = quiz.hasQuizFor(concept.concept_id);
    els.btnOpenQuiz.disabled = isDone || !hasQuiz;
    els.btnOpenQuiz.textContent = isDone
      ? "✅ Đã hoàn thành khái niệm này"
      : hasQuiz
      ? "🧠 Làm Quiz kiểm tra (AI)"
      : "⏳ Chưa có câu hỏi cho khái niệm này";
  }

  /** Hiện chi tiết khái niệm ngay trong panel Graph khi bấm 1 node — không đụng tới video. */
  function renderNodeDetailCard(node) {
    els.nodeDetailCard.hidden = false;
    els.nodeDetailName.textContent = node.name;
    els.nodeDetailFormula.textContent = node.formula || "";
    els.nodeDetailFormula.hidden = !node.formula;
    els.nodeDetailDesc.textContent = node.description || "Chưa có mô tả cho khái niệm này.";

    renderNodeEvidence(node);
    renderNodeRelations(node);

    els.nodeDetailSource.textContent =
      node.start_time != null
        ? `📍 Nguồn: phút ${formatSec(node.start_time)} trong video${node.slide != null ? " · Slide " + node.slide : ""}`
        : node.slide != null
        ? `📍 Nguồn: Slide ${node.slide}`
        : "";
    if (node.mastery_score != null) {
      els.nodeDetailMastery.textContent = `Độ hiểu: ${Math.round(node.mastery_score * 100)}%`;
      els.nodeDetailMastery.className = `mastery-pill mastery-pill--${node.mastery_state}`;
      els.nodeDetailMastery.hidden = false;
    } else {
      els.nodeDetailMastery.hidden = true;
    }
  }

  /**
   * Mô tả của backend chỉ là 1 câu viết sẵn theo từ khoá, không đọc transcript
   * -> hời hợt. Bù lại bằng trích dẫn THẬT lấy từ transcript (data-loader.js đã
   * so khớp cụm từ sẵn, không suy diễn thêm) kèm mốc giây — bấm vào là tua video
   * ngay tới đúng chỗ đó, biến "chi tiết khái niệm" thành bằng chứng cụ thể thay
   * vì một câu chung chung.
   */
  function renderNodeEvidence(node) {
    const evidence = node.evidence || [];
    if (!evidence.length) {
      els.nodeDetailEvidenceBlock.hidden = true;
      return;
    }
    els.nodeDetailEvidence.innerHTML = evidence
      .map(
        ev => `
        <button type="button" class="evidence-item" data-time="${ev.start_time}">
          <span class="evidence-time">${formatSec(ev.start_time)}</span>
          <span class="evidence-text">${escapeHtml(ev.text)}</span>
        </button>`
      )
      .join("");
    els.nodeDetailEvidenceBlock.hidden = false;
    els.nodeDetailEvidence.querySelectorAll(".evidence-item").forEach(btn => {
      btn.addEventListener("click", () => {
        const sec = Number(btn.dataset.time);
        if (!Number.isNaN(sec)) {
          player.seekTo(sec);
          switchTab("video");
        }
      });
    });
  }

  /**
   * Liệt kê quan hệ của khái niệm đang mở: cái gì phải học trước nó, và học nó
   * xong thì mở ra cái gì — đọc trực tiếp từ edges nên luôn khớp với mũi tên vẽ
   * trên graph. Bấm vào một khái niệm liên quan thì nhảy thẳng sang thẻ của nó.
   */
  function renderNodeRelations(node) {
    const incoming = data.edges.filter(e => e.target_concept_id === node.concept_id);
    const outgoing = data.edges.filter(e => e.source_concept_id === node.concept_id);
    if (!incoming.length && !outgoing.length) {
      els.nodeDetailLinksBlock.hidden = true;
      return;
    }

    const chip = (otherId, text) => {
      const other = nodeById.get(otherId);
      if (!other) return "";
      return `<button type="button" class="relation-chip" data-concept="${escapeHtml(otherId)}">${escapeHtml(text)} <strong>${escapeHtml(other.name)}</strong></button>`;
    };

    const html = [
      ...incoming.map(e => chip(e.source_concept_id, e.label || "cần hiểu trước:")),
      ...outgoing.map(e => chip(e.target_concept_id, "→ mở ra:"))
    ]
      .filter(Boolean)
      .join("");

    els.nodeDetailLinks.innerHTML = html;
    els.nodeDetailLinksBlock.hidden = !html;
    els.nodeDetailLinks.querySelectorAll(".relation-chip").forEach(btn => {
      btn.addEventListener("click", () => {
        const target = nodeById.get(btn.dataset.concept);
        if (target) renderNodeDetailCard(target);
      });
    });
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
  }

  function formatSec(totalSec) {
    const m = Math.floor(totalSec / 60);
    const s = Math.floor(totalSec % 60);
    return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s}`;
  }

  function renderConceptDetail(concept) {
    els.conceptName.textContent = concept.name;
    els.conceptDesc.textContent = concept.description || "";
    els.conceptFormula.textContent = concept.formula || "";
    els.conceptFormula.hidden = !concept.formula;
    if (concept.mastery_score != null) {
      els.conceptMastery.textContent = `Độ hiểu: ${Math.round(concept.mastery_score * 100)}%`;
      els.conceptMastery.className = `mastery-pill mastery-pill--${concept.mastery_state}`;
      els.conceptMastery.hidden = false;
    } else {
      els.conceptMastery.hidden = true;
    }
  }

  /** Duyệt ngược đồ thị (BFS trên prerequisite) tìm khái niệm gốc rễ yếu nhất. */
  function findWeakestPrerequisite(conceptId) {
    const parentsOf = new Map();
    data.edges.forEach(e => {
      if (!parentsOf.has(e.target_concept_id)) parentsOf.set(e.target_concept_id, []);
      parentsOf.get(e.target_concept_id).push(e.source_concept_id);
    });

    const visited = new Set([conceptId]);
    let queue = parentsOf.get(conceptId) || [];
    let weakest = null;

    while (queue.length) {
      const id = queue.shift();
      if (visited.has(id)) continue;
      visited.add(id);
      const node = nodeById.get(id);
      if (node && node.mastery_score != null && node.mastery_score < 0.5) {
        if (!weakest || node.mastery_score < weakest.mastery_score) weakest = node;
      }
      queue = queue.concat(parentsOf.get(id) || []);
    }
    return weakest;
  }

  function renderRecommendation(concept) {
    if (concept.mastery_state !== "weak") {
      els.recommendationBox.hidden = true;
      return;
    }
    const weakest = findWeakestPrerequisite(concept.concept_id);
    const target = weakest || concept; // không tìm được gốc rễ khác -> chính nó là điểm cần ôn
    els.recommendationBox.hidden = false;
    els.recommendationBox.innerHTML = `
      <div class="rec-title">⚠️ Phát hiện lỗ hổng kiến thức</div>
      <div class="rec-body">
        <strong>${concept.name}</strong> đang yếu (${Math.round(concept.mastery_score * 100)}%).
        ${
          weakest
            ? `Gốc rễ có thể do chưa vững <strong>${weakest.name}</strong> (${Math.round(weakest.mastery_score * 100)}%).`
            : "Nên ôn lại chính khái niệm này."
        }
      </div>
      <button class="btn-jump-source" data-target="${target.concept_id}">↩ Ôn lại: ${target.name}</button>
    `;
    els.recommendationBox.querySelector(".btn-jump-source").addEventListener("click", () => {
      if (target.start_time != null) player.seekTo(target.start_time);
    });
  }

  function handleQuizAnswered({ concept, isCorrect }) {
    if (!isCorrect) return;
    const newScore = Math.min(1, (concept.mastery_score ?? 0) + 0.35);
    const newState = newScore >= 0.85 ? "mastered" : newScore >= 0.5 ? "learning" : "weak";
    concept.mastery_score = newScore;
    concept.mastery_state = newState;
    graph.updateNodeMastery(concept.concept_id, newScore, newState);
    renderConceptDetail(concept);
    renderRecommendation(concept);
    updateQuizButtonState(concept); // vừa đạt 100% -> disable nút ngay, không cần đợi video nhích tiếp
  }
})();
