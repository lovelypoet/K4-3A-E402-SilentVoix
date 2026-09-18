/** Grounded quiz client. Quiz content comes from the server API for real lessons. */
function createQuizController({ modalEl, onAnswered, apiBaseUrl, getLessonId }) {
  const bodyEl = modalEl.querySelector(".quiz-body");
  let currentConcept = null, currentQuiz = null, selected = null, difficulty = "medium";
  modalEl.querySelectorAll("[data-quiz-close]").forEach(btn => btn.addEventListener("click", close));

  async function open(concept) {
    currentConcept = concept; currentQuiz = null; selected = null;
    modalEl.classList.add("show");
    bodyEl.innerHTML = `<div class="quiz-empty">Đang tạo quiz grounded từ nguồn bài học...</div>`;
    try {
      const response = await fetch(`${apiBaseUrl}/quiz/generate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lesson_id: getLessonId(), concept_id: concept.concept_id, difficulty })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || `Quiz API lỗi ${response.status}`);
      currentQuiz = result; render();
    } catch (error) {
      bodyEl.innerHTML = `<div class="quiz-empty">Quiz generation is temporarily unavailable. Please try again.</div>`;
    }
  }
  function close() { modalEl.classList.remove("show"); }
  function render() {
    if (!currentQuiz || currentQuiz.decision !== "GENERATE_QUIZ" || !currentQuiz.validation?.passed) {
      const message = currentQuiz?.decision === "REFUSE_UNGROUNDED" || currentQuiz?.decision === "DISAMBIGUATE"
        ? "No sufficiently supported source evidence was found for this quiz."
        : "Quiz generation is temporarily unavailable. Please try again.";
      bodyEl.innerHTML = `<div class="quiz-empty">${message}</div>`;
      return;
    }
    const citationText = (currentQuiz.citations || []).map(c => c.page != null ? `Trang ${c.page}` : c.slide != null ? `Slide ${c.slide}` : c.start_time != null ? `Video ${formatTime(c.start_time)}–${formatTime(c.end_time || c.start_time)}` : c.chunk_id).join(" · ");
    bodyEl.innerHTML = `<label class="quiz-difficulty">Độ khó:
      <select id="quiz-difficulty-select"><option value="easy" ${difficulty === "easy" ? "selected" : ""}>Easy</option><option value="medium" ${difficulty === "medium" ? "selected" : ""}>Medium</option><option value="hard" ${difficulty === "hard" ? "selected" : ""}>Hard</option></select></label>
      <div class="citation-box"><strong>Nguồn:</strong> ${escapeHtml(citationText)} · <em>${escapeHtml(currentQuiz.concept_label)}</em></div>
      <div class="quiz-question-text">${escapeHtml(currentQuiz.question)}</div>
      <div class="options-group">${currentQuiz.options.map(o => `<div class="quiz-option" data-id="${escapeHtml(o.id)}"><span>${escapeHtml(o.id)}.</span> ${escapeHtml(o.text)}</div>`).join("")}</div>
      <div class="quiz-explanation" hidden></div>`;
    bodyEl.querySelector("#quiz-difficulty-select").addEventListener("change", e => { difficulty = e.target.value; });
    bodyEl.querySelectorAll(".quiz-option").forEach(el => el.addEventListener("click", () => {
      bodyEl.querySelectorAll(".quiz-option").forEach(o => o.classList.remove("selected")); el.classList.add("selected"); selected = el.dataset.id;
    }));
  }
  function submit() {
    if (!currentQuiz || selected == null) { alert("Vui lòng chọn 1 đáp án!"); return; }
    const correct = selected === currentQuiz.correct_option;
    bodyEl.querySelector(`.quiz-option[data-id="${selected}"]`).classList.add(correct ? "correct" : "wrong");
    const explanation = bodyEl.querySelector(".quiz-explanation"); explanation.textContent = currentQuiz.explanation || ""; explanation.hidden = false;
    onAnswered({ concept: currentConcept, quiz: currentQuiz, isCorrect: correct });
    if (correct) setTimeout(close, 1200);
  }
  modalEl.querySelector("[data-quiz-submit]").addEventListener("click", submit);
  return { open, close, hasQuizFor: () => true };
}
function formatTime(totalSec) { const value = Number(totalSec || 0), m = Math.floor(value / 60), s = Math.floor(value % 60); return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`; }
function escapeHtml(value) { return String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c])); }
