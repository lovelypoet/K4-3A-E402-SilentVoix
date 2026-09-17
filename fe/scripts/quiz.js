/**
 * quiz.js
 * -----------------------------------------------------------------------
 * Modal "Grounded Quiz" — câu hỏi luôn kèm trích dẫn nguồn (slide/giây).
 *
 * HIỆN TẠI: lấy câu hỏi từ quiz_bank trong file mock (đáng tin cậy, không
 * phụ thuộc mạng/API key — hợp cho việc dựng UI trước).
 *
 * SAU NÀY KHI NỐI AI/BACKEND THẬT: sửa hàm getQuizForConcept() bên dưới để
 * gọi API sinh quiz thật (ví dụ POST {BACKEND_BASE_URL}/quiz/generate) thay
 * vì đọc quizBank — phần render modal / retry-logic không cần đổi gì.
 */

function createQuizController({ modalEl, quizBank, onAnswered }) {
  const bodyEl = modalEl.querySelector(".quiz-body");
  const closeButtons = modalEl.querySelectorAll("[data-quiz-close]");
  let currentConcept = null;
  let currentQuiz = null;
  let selected = null;

  closeButtons.forEach(btn => btn.addEventListener("click", close));

  function open(concept) {
    currentConcept = concept;
    currentQuiz = getQuizForConcept(concept);
    selected = null;
    modalEl.classList.add("show");
    render();
  }

  function close() {
    modalEl.classList.remove("show");
  }

  /** Nguồn câu hỏi — đổi chỗ này khi nối AI/backend thật (xem docstring trên đầu file). */
  function getQuizForConcept(concept) {
    const list = quizBank[concept.concept_id];
    if (list && list.length) return list[Math.floor(Math.random() * list.length)];
    return null;
  }

  function render() {
    if (!currentQuiz) {
      bodyEl.innerHTML = `
        <div class="quiz-empty">Chưa có câu hỏi mẫu cho khái niệm này trong bộ mock. Hãy thử một node khác (Regression, Loss Function, Gradient Descent).</div>
      `;
      return;
    }
    const citation = `Slide ${currentConcept.slide ?? "?"}${
      currentConcept.start_time != null ? " · " + formatTime(currentConcept.start_time) : ""
    }`;
    const optionsHtml = currentQuiz.options
      .map(
        (opt, i) => `
        <div class="quiz-option" data-index="${i}">
          <span>${String.fromCharCode(65 + i)}.</span> ${opt}
        </div>`
      )
      .join("");

    bodyEl.innerHTML = `
      <div class="citation-box">
        <strong>Nguồn xác thực (Grounding):</strong> ${citation} · <em>${currentConcept.name}</em>
      </div>
      <div class="quiz-question-text">${currentQuiz.question}</div>
      <div class="options-group">${optionsHtml}</div>
    `;

    bodyEl.querySelectorAll(".quiz-option").forEach(el => {
      el.addEventListener("click", () => {
        bodyEl.querySelectorAll(".quiz-option").forEach(o => o.classList.remove("selected"));
        el.classList.add("selected");
        selected = Number(el.dataset.index);
      });
    });
  }

  function submit() {
    if (selected == null) {
      alert("Vui lòng chọn 1 đáp án!");
      return;
    }
    const isCorrect = selected === currentQuiz.correct_option;
    const selectedEl = bodyEl.querySelector(`.quiz-option[data-index="${selected}"]`);

    if (isCorrect) {
      selectedEl.classList.add("correct");
      onAnswered({ concept: currentConcept, quiz: currentQuiz, isCorrect: true });
      setTimeout(close, 800);
    } else {
      // Sai thì GIỮ NGUYÊN modal + câu hỏi để chọn lại, không đóng, không đổi câu hỏi mới.
      selectedEl.classList.add("wrong");
      onAnswered({ concept: currentConcept, quiz: currentQuiz, isCorrect: false });
      selected = null;
    }
  }

  modalEl.querySelector("[data-quiz-submit]").addEventListener("click", submit);

  return { open, close };
}

function formatTime(totalSec) {
  const m = Math.floor(totalSec / 60);
  const s = Math.floor(totalSec % 60);
  return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s}`;
}
