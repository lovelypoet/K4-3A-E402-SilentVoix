/**
 * graph.js
 * -----------------------------------------------------------------------
 * Vẽ Knowledge Graph (Semantic Map) bằng SVG thuần — GIỮ NGUYÊN cách tiếp
 * cận của bản index.html cũ (node tròn + nhãn + %, cạnh nối cong, halo cho
 * node đang active, legend theo màu + chữ). Khác biệt: thay vì toạ độ vẽ
 * tay cố định, layout được TÍNH TỰ ĐỘNG (BFS theo tầng) để khi nối dữ liệu
 * thật từ backend (nodes/edges đổi khác) đồ thị vẫn tự sắp xếp hợp lý,
 * không cần sửa code vẽ.
 */

const MASTERY_COLOR = {
  mastered:    { stroke: "#10b981", fill: "#ecfdf5", text: "#065f46", label: "Đã vững" },
  learning:    { stroke: "#d97706", fill: "#fffbeb", text: "#92400e", label: "Đang học" },
  weak:        { stroke: "#e11d48", fill: "#fff1f2", text: "#9f1239", label: "Yếu" },
  not_learned: { stroke: "#94a3b8", fill: "#f8fafc", text: "#475569", label: "Chưa học" },
  current:     { stroke: "#2563eb", fill: "#eff6ff", text: "#1e3a8a", label: "Đang xem" }
};

const NODE_R = 34;

/** BFS theo tầng: node không có cạnh nào trỏ vào là gốc (layer 0). */
function computeLayout(nodes, edges, width, height) {
  const incoming = new Map(nodes.map(n => [n.concept_id, 0]));
  edges.forEach(e => incoming.set(e.target_concept_id, (incoming.get(e.target_concept_id) || 0) + 1));

  const childrenOf = new Map(nodes.map(n => [n.concept_id, []]));
  edges.forEach(e => {
    if (childrenOf.has(e.source_concept_id)) childrenOf.get(e.source_concept_id).push(e.target_concept_id);
  });

  const layerOf = new Map();
  const roots = nodes.filter(n => (incoming.get(n.concept_id) || 0) === 0).map(n => n.concept_id);
  let frontier = roots.length ? roots : [nodes[0]?.concept_id].filter(Boolean);
  let depth = 0;
  const visited = new Set();
  while (frontier.length) {
    const next = [];
    frontier.forEach(id => {
      if (visited.has(id)) return;
      visited.add(id);
      layerOf.set(id, depth);
      (childrenOf.get(id) || []).forEach(childId => next.push(childId));
    });
    frontier = next;
    depth++;
  }
  // Node mồ côi (không tới được từ root) -> xếp cuối
  nodes.forEach(n => { if (!layerOf.has(n.concept_id)) layerOf.set(n.concept_id, depth); });

  const maxLayer = Math.max(0, ...layerOf.values());
  const byLayer = new Map();
  nodes.forEach(n => {
    const l = layerOf.get(n.concept_id);
    if (!byLayer.has(l)) byLayer.set(l, []);
    byLayer.get(l).push(n.concept_id);
  });

  const positions = {};
  const marginY = 50;
  const usableH = Math.max(1, height - marginY * 2);
  byLayer.forEach((ids, layer) => {
    const y = marginY + (maxLayer === 0 ? usableH / 2 : (usableH * layer) / maxLayer);
    const step = width / (ids.length + 1);
    ids.forEach((id, i) => {
      positions[id] = { x: step * (i + 1), y };
    });
  });
  return positions;
}

/**
 * Vẽ toàn bộ graph vào 1 phần tử <svg>. Trả về object điều khiển
 * (setActiveConcept, updateNodeMastery) để app.js gọi khi video chạy /
 * học viên làm quiz xong.
 */
function renderGraph(svgEl, nodes, edges) {
  const width = svgEl.clientWidth || 360;
  const height = svgEl.clientHeight || 480;
  svgEl.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svgEl.innerHTML = "";

  const positions = computeLayout(nodes, edges, width, height);
  const nodeById = new Map(nodes.map(n => [n.concept_id, n]));

  const svgNS = "http://www.w3.org/2000/svg";
  const edgeLayer = document.createElementNS(svgNS, "g");
  const haloLayer = document.createElementNS(svgNS, "g");
  const nodeLayer = document.createElementNS(svgNS, "g");
  svgEl.append(edgeLayer, haloLayer, nodeLayer);

  // --- Cạnh nối (prerequisite) ---
  const edgeEls = []; // để revealUpTo() biết cạnh nào nối node nào mà ẩn/hiện đúng lúc
  edges.forEach(e => {
    const from = positions[e.source_concept_id];
    const to = positions[e.target_concept_id];
    if (!from || !to) return;
    const midY = (from.y + to.y) / 2;
    const path = document.createElementNS(svgNS, "path");
    path.setAttribute(
      "d",
      `M ${from.x} ${from.y} C ${from.x} ${midY}, ${to.x} ${midY}, ${to.x} ${to.y}`
    );
    path.setAttribute("class", "kg-edge kg-edge--hidden"); // ẩn mặc định, revealUpTo() sẽ hiện dần
    path.setAttribute("stroke", "#d97706");
    path.setAttribute("stroke-width", "2");
    path.setAttribute("fill", "none");
    path.setAttribute("opacity", "0.55");
    edgeLayer.appendChild(path);
    edgeEls.push({ path, source: e.source_concept_id, target: e.target_concept_id });
  });

  // --- Halo (viền active), tạo sẵn 1 vòng ẩn để bật/tắt cho gọn ---
  const halo = document.createElementNS(svgNS, "circle");
  halo.setAttribute("r", NODE_R + 8);
  halo.setAttribute("fill", "none");
  halo.setAttribute("stroke", MASTERY_COLOR.current.stroke);
  halo.setAttribute("stroke-width", "3");
  halo.setAttribute("opacity", "0");
  halo.style.transition = "cx 0.35s ease, cy 0.35s ease, opacity 0.2s ease";
  haloLayer.appendChild(halo);

  // --- Node ---
  const nodeEls = {};
  nodes.forEach(n => {
    const pos = positions[n.concept_id];
    if (!pos) return;
    const g = document.createElementNS(svgNS, "g");
    g.setAttribute("class", "kg-node kg-node--hidden"); // ẩn mặc định, revealUpTo() sẽ hiện dần theo video
    g.style.cursor = "pointer";
    g.dataset.conceptId = n.concept_id;

    const palette = MASTERY_COLOR[n.mastery_state] || MASTERY_COLOR.not_learned;
    const circle = document.createElementNS(svgNS, "circle");
    circle.setAttribute("cx", pos.x);
    circle.setAttribute("cy", pos.y);
    circle.setAttribute("r", NODE_R);
    circle.setAttribute("fill", palette.fill);
    circle.setAttribute("stroke", palette.stroke);
    circle.setAttribute("stroke-width", "2.5");

    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", pos.x);
    label.setAttribute("y", pos.y - 4);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("font-size", "10.5");
    label.setAttribute("font-weight", "600");
    label.setAttribute("fill", palette.text);
    label.textContent = wrapShort(n.name);

    const scoreText = document.createElementNS(svgNS, "text");
    scoreText.setAttribute("x", pos.x);
    scoreText.setAttribute("y", pos.y + 12);
    scoreText.setAttribute("text-anchor", "middle");
    scoreText.setAttribute("font-size", "11");
    scoreText.setAttribute("font-weight", "700");
    scoreText.setAttribute("fill", palette.text);
    scoreText.textContent = n.mastery_score != null ? `${Math.round(n.mastery_score * 100)}%` : "—";

    g.append(circle, label, scoreText);
    nodeLayer.appendChild(g);
    nodeEls[n.concept_id] = { g, circle, label, scoreText, pos };
  });

  let activeId = null;

  function setActiveConcept(conceptId) {
    activeId = conceptId;
    const target = nodeEls[conceptId];
    Object.values(nodeEls).forEach(({ g }) => g.classList.remove("kg-node--active"));
    if (!target) {
      halo.setAttribute("opacity", "0");
      return;
    }
    target.g.classList.add("kg-node--active");
    halo.setAttribute("cx", target.pos.x);
    halo.setAttribute("cy", target.pos.y);
    halo.setAttribute("opacity", "1");
  }

  function updateNodeMastery(conceptId, masteryScore, masteryState) {
    const node = nodeById.get(conceptId);
    const target = nodeEls[conceptId];
    if (!node || !target) return;
    node.mastery_score = masteryScore;
    node.mastery_state = masteryState;
    const palette = MASTERY_COLOR[masteryState] || MASTERY_COLOR.not_learned;
    target.circle.setAttribute("fill", palette.fill);
    target.circle.setAttribute("stroke", palette.stroke);
    target.label.setAttribute("fill", palette.text);
    target.scoreText.setAttribute("fill", palette.text);
    target.scoreText.textContent = masteryScore != null ? `${Math.round(masteryScore * 100)}%` : "—";
  }

  function onNodeClick(handler) {
    nodeLayer.addEventListener("click", (evt) => {
      const g = evt.target.closest(".kg-node");
      // Node đang bị ẩn (chưa xem tới đoạn video tương ứng) thì không cho bấm điều hướng tới.
      if (g && g.dataset.conceptId && !g.classList.contains("kg-node--hidden")) {
        handler(g.dataset.conceptId);
      }
    });
  }

  /**
   * Hiện dần graph theo tiến trình video: node nào có start_time <= currentSec
   * (đoạn đó đã "xem tới") thì hiện; còn lại vẫn ẩn — giống sơ đồ tư duy dựng
   * dần chứ không lộ hết quan hệ kiến thức ngay từ đầu. 1 cạnh chỉ hiện khi
   * CẢ HAI đầu (nguồn + đích) đều đã hiện.
   * Lưu ý: node không có start_time (VD nhánh phụ "chưa học trong bài") sẽ
   * không bao giờ tự hiện qua cơ chế này.
   */
  function revealUpTo(currentSec) {
    Object.entries(nodeEls).forEach(([conceptId, { g }]) => {
      const node = nodeById.get(conceptId);
      const revealed = node.start_time != null && currentSec >= node.start_time;
      g.classList.toggle("kg-node--hidden", !revealed);
    });
    edgeEls.forEach(({ path, source, target }) => {
      const sourceNode = nodeById.get(source);
      const targetNode = nodeById.get(target);
      const sourceRevealed = !!sourceNode && sourceNode.start_time != null && currentSec >= sourceNode.start_time;
      const targetRevealed = !!targetNode && targetNode.start_time != null && currentSec >= targetNode.start_time;
      path.classList.toggle("kg-edge--hidden", !(sourceRevealed && targetRevealed));
    });
  }

  return { setActiveConcept, updateNodeMastery, onNodeClick, revealUpTo, getActiveConcept: () => activeId };
}

function wrapShort(name) {
  // Cắt tên dài cho vừa trong node tròn (label đầy đủ vẫn hiện ở panel chi tiết bên dưới)
  return name.length > 14 ? name.slice(0, 13) + "…" : name;
}
