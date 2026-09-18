/**
 * video-player.js
 * -----------------------------------------------------------------------
 * Điều khiển player bên trái. Tự chọn 1 trong 3 chế độ tuỳ "videoUrl":
 *
 *   - videoUrl = null              -> MÔ PHỎNG (timer giả lập, chưa có video thật)
 *   - videoUrl = link YouTube      -> nhúng qua YouTube IFrame Player API
 *   - videoUrl = link file (.mp4…) -> thẻ <video> thường
 *
 * Cả 3 chế độ đều expose CÙNG 1 API (play/pause/seekTo/getCurrentSec) và
 * cùng bắn onTimeUpdate(sec) — app.js/graph.js không cần biết đang chạy chế
 * độ nào.
 */

function createVideoPlayer({ container, durationSec, videoUrl, onTimeUpdate }) {
  container.innerHTML = "";

  // Lesson dạng slide/PDF (không có video) trả duration_seconds = 0 -> tránh chia cho 0
  // (NaN% thanh tiến trình, tick() auto-pause ngay lập tức vì 0 >= 0 luôn đúng).
  if (!durationSec) durationSec = 1;

  const youtubeId = videoUrl ? extractYouTubeId(videoUrl) : null;
  const mode = youtubeId ? "youtube" : videoUrl ? "file" : "mock";

  let currentSec = 0;
  let playing = false;
  let speed = 1;
  let timer = null;
  let videoEl = null;
  let ytPlayer = null;
  let ytPollTimer = null;
  let placeholderIcon = null;

  // QUAN TRỌNG: khung video (stage) và thanh điều khiển (controls) là 2 khối
  // TÁCH BIỆT, không lồng đè lên nhau (placeholder "inset:0" từng phủ kín cả
  // thanh điều khiển bên dưới, chặn hết click nút 1x/4x/12x — đã sửa bằng
  // cách tách stage riêng, xem lịch sử sửa lỗi ở commit trước).
  const stage = document.createElement("div");
  stage.className = "video-stage";
  container.appendChild(stage);

  if (mode === "youtube") {
    const ytMount = document.createElement("div");
    ytMount.className = "video-yt-mount";
    stage.appendChild(ytMount);
    loadYouTubeAPI().then(YT => {
      ytPlayer = new YT.Player(ytMount, {
        videoId: youtubeId,
        playerVars: {
          controls: 1,
          modestbranding: 1,
          rel: 0,
          playsinline: 1,
          // Thiếu "origin" khiến YouTube không nhận diện được trang đang nhúng (đặc biệt khi
          // mở file qua file:// thay vì qua server thật) -> trả lỗi EMBEDDER_IDENTITY_MISSING_REFERRER
          // và tự hiện 1 video gợi ý khác thay vì video mình yêu cầu, KHÔNG báo lỗi JS nào để bắt được.
          origin: window.location.origin
        },
        events: {
          onReady: () => {
            durationSec = ytPlayer.getDuration() || durationSec; // ưu tiên thời lượng thật từ YouTube
            renderProgress();
            startYtPolling();
          },
          onStateChange: (evt) => {
            const YTState = window.YT.PlayerState;
            if (evt.data === YTState.PLAYING) setPlayingUI(true);
            else if (evt.data === YTState.PAUSED || evt.data === YTState.ENDED) setPlayingUI(false);
          }
        }
      });
    });
  } else if (mode === "file") {
    videoEl = document.createElement("video");
    videoEl.src = videoUrl;
    videoEl.className = "video-real";
    videoEl.addEventListener("timeupdate", () => {
      currentSec = videoEl.currentTime;
      onTimeUpdate(currentSec);
      renderProgress();
    });
    stage.appendChild(videoEl);
  } else {
    const placeholder = document.createElement("div");
    placeholder.className = "video-placeholder";
    placeholder.title = "Bấm để Play/Pause";
    placeholder.innerHTML = `
      <div class="video-placeholder-icon">▶</div>
      <div class="video-placeholder-text">Video mô phỏng — bấm vào đây hoặc nút Play bên dưới để chạy</div>
    `;
    placeholderIcon = placeholder.querySelector(".video-placeholder-icon");
    placeholder.addEventListener("click", () => (playing ? pause() : play()));
    stage.appendChild(placeholder);
  }

  const controls = document.createElement("div");
  controls.className = "video-controls";
  controls.innerHTML = `
    <button class="btn-play-pause" type="button" aria-label="Play/Pause">▶</button>
    <div class="video-progress-track" tabindex="0" role="slider" aria-label="Tua video">
      <div class="video-progress-fill"></div>
      <div class="video-progress-handle"></div>
    </div>
    <div class="video-time-label">00:00 / ${formatTime(durationSec)}</div>
    <div class="video-speed-group">
      <button class="speed-btn active" data-speed="1">1x</button>
      <button class="speed-btn" data-speed="4">4x</button>
      <button class="speed-btn" data-speed="12">12x</button>
    </div>
  `;
  // controls là ANH EM của stage (cùng cấp), KHÔNG nằm trong stage -> không thể bị
  // placeholder/video/YouTube đè lên.
  container.appendChild(controls);

  const playBtn = controls.querySelector(".btn-play-pause");
  const track = controls.querySelector(".video-progress-track");
  const fill = controls.querySelector(".video-progress-fill");
  const handle = controls.querySelector(".video-progress-handle");
  const timeLabel = controls.querySelector(".video-time-label");
  const speedBtns = [...controls.querySelectorAll(".speed-btn")];

  function formatTime(totalSec) {
    const m = Math.floor(totalSec / 60);
    const s = Math.floor(totalSec % 60);
    return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s}`;
  }

  function renderProgress() {
    const pct = Math.min(100, (currentSec / durationSec) * 100);
    fill.style.width = `${pct}%`;
    handle.style.left = `${pct}%`;
    timeLabel.textContent = `${formatTime(currentSec)} / ${formatTime(durationSec)}`;
  }

  function setPlayingUI(isPlaying) {
    playing = isPlaying;
    playBtn.textContent = isPlaying ? "⏸" : "▶";
    if (placeholderIcon) placeholderIcon.textContent = isPlaying ? "⏸" : "▶";
  }

  function tick() {
    // Chế độ mock: tự cộng dồn thời gian giả lập.
    currentSec = Math.min(durationSec, currentSec + 0.2 * speed);
    onTimeUpdate(currentSec);
    renderProgress();
    if (currentSec >= durationSec) pause();
  }

  /** YouTube không bắn timeupdate liên tục như <video> -> phải tự polling. */
  function startYtPolling() {
    clearInterval(ytPollTimer);
    ytPollTimer = setInterval(() => {
      if (!ytPlayer || typeof ytPlayer.getCurrentTime !== "function") return;
      currentSec = ytPlayer.getCurrentTime();
      onTimeUpdate(currentSec);
      renderProgress();
    }, 250);
  }

  function play() {
    setPlayingUI(true);
    if (mode === "youtube") {
      if (ytPlayer) { ytPlayer.setPlaybackRate(speed); ytPlayer.playVideo(); }
    } else if (mode === "file") {
      videoEl.playbackRate = speed;
      videoEl.play();
    } else {
      clearInterval(timer);
      timer = setInterval(tick, 200);
    }
  }

  function pause() {
    setPlayingUI(false);
    if (mode === "youtube") { if (ytPlayer) ytPlayer.pauseVideo(); }
    else if (mode === "file") videoEl.pause();
    else clearInterval(timer);
  }

  function seekTo(sec) {
    currentSec = Math.max(0, Math.min(durationSec, sec));
    if (mode === "youtube") { if (ytPlayer) ytPlayer.seekTo(currentSec, true); }
    else if (mode === "file") videoEl.currentTime = currentSec;
    onTimeUpdate(currentSec);
    renderProgress();
  }

  playBtn.addEventListener("click", () => (playing ? pause() : play()));

  track.addEventListener("click", (evt) => {
    const rect = track.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (evt.clientX - rect.left) / rect.width));
    seekTo(pct * durationSec);
  });

  speedBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      speed = Number(btn.dataset.speed);
      speedBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      if (mode === "youtube" && ytPlayer) ytPlayer.setPlaybackRate(speed);
      if (mode === "file" && videoEl) videoEl.playbackRate = speed;
    });
  });

  renderProgress();

  /**
   * Dọn dẹp player này hoàn toàn — BẮT BUỘC phải gọi trước khi tạo player mới
   * (VD đổi link video), nếu không interval polling của YouTube (250ms) vẫn
   * chạy nền song song với player mới, 2 bên liên tục ghi đè thông tin của
   * nhau -> tên/nội dung bị nháy qua lại liên tục.
   */
  function destroy() {
    clearInterval(timer);
    clearInterval(ytPollTimer);
    if (ytPlayer && typeof ytPlayer.destroy === "function") ytPlayer.destroy();
    if (videoEl) { videoEl.pause(); videoEl.src = ""; }
  }

  return {
    play,
    pause,
    seekTo,
    getCurrentSec: () => currentSec,
    destroy
  };
}

/** Nhận diện link YouTube (watch?v=, youtu.be/, embed/) và lấy ra video ID 11 ký tự. */
function extractYouTubeId(url) {
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]{11})/);
  return match ? match[1] : null;
}

// Nạp YouTube IFrame API đúng 1 lần cho toàn trang, dùng lại nếu đã nạp rồi.
let _youtubeApiPromise = null;
function loadYouTubeAPI() {
  if (window.YT && window.YT.Player) return Promise.resolve(window.YT);
  if (_youtubeApiPromise) return _youtubeApiPromise;
  _youtubeApiPromise = new Promise((resolve) => {
    const previousCallback = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      if (typeof previousCallback === "function") previousCallback();
      resolve(window.YT);
    };
    const tag = document.createElement("script");
    tag.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(tag);
  });
  return _youtubeApiPromise;
}
