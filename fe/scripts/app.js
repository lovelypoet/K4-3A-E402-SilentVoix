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

  let data;
  try {
    data = await loadLessonData();
  } catch (err) {
    els.videoContainer.innerHTML = `<div class="load-error">Không tải được dữ liệu bài học: ${err.message}</div>`;
    return;
  }

  els.lessonTitle.textContent = data.title;
  const nodeById = new Map(data.nodes.map(n => [n.concept_id, n]));

  const graph = renderGraph(els.graphSvg, data.nodes, data.edges);

  const quiz = createQuizController({
    modalEl: els.quizModal,
    quizBank: data.quizBank,
    onAnswered: handleQuizAnswered
  });

  // "let" vì loadVideoFromInput() sẽ tạo lại player mới khi đổi link — không dùng "const"
  let player = createVideoPlayer({
    container: els.videoContainer,
    durationSec: data.durationSec,
    videoUrl: data.videoUrl,
    onTimeUpdate: handleTimeUpdate
  });
  if (data.videoUrl) els.videoLinkInput.value = data.videoUrl;

  /**
   * Ô dán link (công cụ test/demo, KHÔNG phải tính năng AI) — đổi video đang
   * xem sang link mới ngay lập tức, không cần sửa code/file mock.
   */
  function loadVideoFromInput() {
    const url = els.videoLinkInput.value.trim();
    if (!url) return;
    player.destroy(); // tắt hẳn player cũ trước — không thì 2 player chạy song song, gây nháy nội dung
    player = createVideoPlayer({
      container: els.videoContainer,
      durationSec: data.durationSec,
      videoUrl: url,
      onTimeUpdate: handleTimeUpdate
    });
    handleTimeUpdate(0); // reset graph/panel chi tiết về đầu video mới
  }
  els.videoLinkLoad.addEventListener("click", loadVideoFromInput);
  els.videoLinkInput.addEventListener("keydown", (evt) => {
    if (evt.key === "Enter") loadVideoFromInput();
  });

  graph.onNodeClick(conceptId => {
    const node = nodeById.get(conceptId);
    if (node) renderNodeDetailCard(node); // chỉ hiện chi tiết, KHÔNG tua video
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
   * Ô dán link PDF slide thật (công cụ test, giống ô link video) — nhúng bằng
   * <iframe>, trình duyệt tự render PDF, không cần thư viện ngoài. Một số PDF
   * chặn nhúng iframe (X-Frame-Options) thì sẽ hiện trắng — lúc đó bấm
   * "Bỏ PDF" để quay lại thẻ mô tả, hoặc thử link PDF khác.
   */
  function loadSlidePdf() {
    const url = els.slideLinkInput.value.trim();
    if (!url) return;
    els.slidePdfFrame.src = url;
    els.slidePdfFrame.hidden = false;
    els.slideGenerated.hidden = true;
    els.slideLinkClear.hidden = false;
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

  // Khởi động ở giây 0
  handleTimeUpdate(0);

  // ---------------------------------------------------------------------

  function findConceptAtTime(sec) {
    return data.nodes.find(n => n.start_time != null && sec >= n.start_time && sec < n.end_time) || data.nodes[0];
  }

  function handleTimeUpdate(sec) {
    graph.revealUpTo(sec); // graph "mọc" dần theo đúng đoạn video đã xem tới
    const concept = findConceptAtTime(sec);
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
   */
  function updateQuizButtonState(concept) {
    const isDone = concept.mastery_score != null && concept.mastery_score >= 1;
    els.btnOpenQuiz.disabled = isDone;
    els.btnOpenQuiz.textContent = isDone ? "✅ Đã hoàn thành khái niệm này" : "🧠 Làm Quiz kiểm tra (AI)";
  }

  /** Hiện chi tiết khái niệm ngay trong panel Graph khi bấm 1 node — không đụng tới video. */
  function renderNodeDetailCard(node) {
    els.nodeDetailCard.hidden = false;
    els.nodeDetailName.textContent = node.name;
    els.nodeDetailFormula.textContent = node.formula || "";
    els.nodeDetailFormula.hidden = !node.formula;
    els.nodeDetailDesc.textContent = node.description || "Chưa có mô tả cho khái niệm này.";
    els.nodeDetailSource.textContent =
      node.slide != null ? `📍 Nguồn: Slide ${node.slide}${node.start_time != null ? " · " + formatSec(node.start_time) : ""}` : "";
    if (node.mastery_score != null) {
      els.nodeDetailMastery.textContent = `Độ hiểu: ${Math.round(node.mastery_score * 100)}%`;
      els.nodeDetailMastery.className = `mastery-pill mastery-pill--${node.mastery_state}`;
      els.nodeDetailMastery.hidden = false;
    } else {
      els.nodeDetailMastery.hidden = true;
    }
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
