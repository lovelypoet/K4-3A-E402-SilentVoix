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

/**
 * Mỗi loại quan hệ có màu + mũi tên riêng. Trước đây mọi cạnh đều là một đường
 * cong cam mảnh, không mũi tên, không nhãn -> nhìn không biết ai phụ thuộc ai,
 * mà "phụ thuộc kiến thức" mới chính là thứ Semantic Map cần nói lên.
 */
const RELATION_STYLE = {
  prerequisite: { color: "#d97706", label: "Cần học trước" },
  part_of:      { color: "#2563eb", label: "Là thành phần của" },
  leads_to:     { color: "#10b981", label: "Dẫn tới" },
  contrast:     { color: "#e11d48", label: "Đối lập / phân biệt" }
};

function relationStyle(type) {
  return RELATION_STYLE[type] || RELATION_STYLE.prerequisite;
}

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
// Hệ toạ độ vẽ CỐ ĐỊNH — không phụ thuộc clientWidth/clientHeight thật của khung.
// Đọc clientWidth ngay lúc script chạy dễ bị sai (DOM/CSS đôi khi chưa "ổn định" kích
// thước, đặc biệt sau khi thêm nhiều khối mới ở trên như media-tabs/video-link-bar),
// ra toạ độ méo rồi bị phóng to biến dạng thành 1 khối chữ chồng lên nhau. Dùng khung
// toạ độ cố định rồi để SVG tự co giãn (viewBox + preserveAspectRatio mặc định) luôn
// đúng tỉ lệ, không bao giờ méo dù panel to nhỏ thế nào.
const GRAPH_VIEW_WIDTH = 900;
const GRAPH_VIEW_HEIGHT = 620;

function renderGraph(svgEl, nodes, edges) {
  const width = GRAPH_VIEW_WIDTH;
  const height = GRAPH_VIEW_HEIGHT;
  svgEl.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svgEl.innerHTML = "";

  const positions = computeLayout(nodes, edges, width, height);
  const nodeById = new Map(nodes.map(n => [n.concept_id, n]));

  const svgNS = "http://www.w3.org/2000/svg";
  const defs = document.createElementNS(svgNS, "defs");
  // Mỗi màu quan hệ cần một marker mũi tên riêng (marker SVG không kế thừa màu của path).
  Object.entries(RELATION_STYLE).forEach(([type, style]) => {
    const marker = document.createElementNS(svgNS, "marker");
    marker.setAttribute("id", `kg-arrow-${type}`);
    marker.setAttribute("viewBox", "0 0 10 10");
    marker.setAttribute("refX", "9");
    marker.setAttribute("refY", "5");
    marker.setAttribute("markerWidth", "6");
    marker.setAttribute("markerHeight", "6");
    marker.setAttribute("orient", "auto-start-reverse");
    const arrowPath = document.createElementNS(svgNS, "path");
    arrowPath.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
    arrowPath.setAttribute("fill", style.color);
    marker.appendChild(arrowPath);
    defs.appendChild(marker);
  });

  const edgeLayer = document.createElementNS(svgNS, "g");
  const edgeLabelLayer = document.createElementNS(svgNS, "g");
  const haloLayer = document.createElementNS(svgNS, "g");
  const nodeLayer = document.createElementNS(svgNS, "g");
  svgEl.append(defs, edgeLayer, edgeLabelLayer, haloLayer, nodeLayer);

  // --- Cạnh nối: có hướng (mũi tên), màu theo loại quan hệ, kèm nhãn chữ ---
  const edgeEls = []; // để revealUpTo() biết cạnh nào nối node nào mà ẩn/hiện đúng lúc
  edges.forEach(e => {
    const from = positions[e.source_concept_id];
    const to = positions[e.target_concept_id];
    if (!from || !to) return;

    const style = relationStyle(e.relation_type);

    // Lùi hai đầu cạnh ra khỏi hình tròn node, nếu không mũi tên bị khuất dưới node đích.
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const len = Math.hypot(dx, dy) || 1;
    const ux = dx / len;
    const uy = dy / len;
    const sx = from.x + ux * (NODE_R + 2);
    const sy = from.y + uy * (NODE_R + 2);
    const ex = to.x - ux * (NODE_R + 9);
    const ey = to.y - uy * (NODE_R + 9);
    const midY = (sy + ey) / 2;

    const path = document.createElementNS(svgNS, "path");
    path.setAttribute("d", `M ${sx} ${sy} C ${sx} ${midY}, ${ex} ${midY}, ${ex} ${ey}`);
    path.setAttribute("class", "kg-edge kg-edge--hidden"); // ẩn mặc định, revealUpTo() sẽ hiện dần
    path.setAttribute("stroke", style.color);
    path.setAttribute("stroke-width", "2.2");
    path.setAttribute("fill", "none");
    path.setAttribute("opacity", "0.75");
    path.setAttribute("marker-end", `url(#kg-arrow-${RELATION_STYLE[e.relation_type] ? e.relation_type : "prerequisite"})`);
    edgeLayer.appendChild(path);

    // Nhãn quan hệ đặt giữa cạnh. Viền trắng (paint-order: stroke) để chữ không
    // bị đường kẻ xuyên qua, đọc được kể cả khi cạnh chạy phía sau.
    let labelEl = null;
    const labelText = (e.label || "").trim();
    if (labelText) {
      labelEl = document.createElementNS(svgNS, "text");
      labelEl.setAttribute("x", (sx + ex) / 2);
      labelEl.setAttribute("y", (sy + ey) / 2 - 3);
      labelEl.setAttribute("text-anchor", "middle");
      labelEl.setAttribute("font-size", "9.5");
      labelEl.setAttribute("font-weight", "600");
      labelEl.setAttribute("fill", style.color);
      labelEl.setAttribute("stroke", "#fffdf7");
      labelEl.setAttribute("stroke-width", "3.5");
      labelEl.setAttribute("paint-order", "stroke");
      labelEl.setAttribute("class", "kg-edge-label kg-edge--hidden");
      labelEl.textContent = labelText.length > 20 ? labelText.slice(0, 19) + "…" : labelText;
      edgeLabelLayer.appendChild(labelEl);
    }

    edgeEls.push({ path, labelEl, source: e.source_concept_id, target: e.target_concept_id });
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

  // Node không nằm trên cạnh nào (kể cả sau khi đã gộp trùng ở data-loader.js)
  // -> vẽ khác biệt (viền đứt nét) để KHÔNG đánh lừa là đã có liên kết, thay vì
  // trộn lẫn với node thật sự thuộc chuỗi phụ thuộc.
  const connectedIds = new Set();
  edges.forEach(e => {
    connectedIds.add(e.source_concept_id);
    connectedIds.add(e.target_concept_id);
  });

  // --- Node ---
  const nodeEls = {};
  nodes.forEach(n => {
    const pos = positions[n.concept_id];
    if (!pos) return;
    const isIsolated = !connectedIds.has(n.concept_id);
    const g = document.createElementNS(svgNS, "g");
    g.setAttribute("class", `kg-node kg-node--hidden${isIsolated ? " kg-node--isolated" : ""}`); // ẩn mặc định, revealUpTo() sẽ hiện dần theo video
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
    if (isIsolated) circle.setAttribute("stroke-dasharray", "4 3");

    // Tên khái niệm có thể dài hơn nhiều so với đường kính hình tròn -> xuống
    // dòng tối đa 3 dòng thay vì để tràn ra ngoài; hết chỗ mà vẫn còn chữ thì
    // cắt bớt và thêm "…" ở dòng cuối.
    const LABEL_LINE_HEIGHT = 10;
    // Tên gộp có dạng "Việt (English)" (xem mergeDuplicateConcepts ở data-loader.js) —
    // bỏ phần trong ngoặc khi hiển thị rút gọn trong vòng tròn, tên đầy đủ vẫn
    // còn nguyên ở thẻ chi tiết khi bấm vào node.
    const compactName = (n.short_label || n.name).replace(/\s*\([^)]*\)\s*$/, "").trim() || n.name;
    const labelLines = wrapNodeLabel(compactName, 10, 3);
    const labelBlockOffset = ((labelLines.length - 1) * LABEL_LINE_HEIGHT) / 2;
    const labelFirstY = pos.y - 4 - labelBlockOffset;

    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", pos.x);
    label.setAttribute("y", labelFirstY);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("font-size", "9.5");
    label.setAttribute("font-weight", "600");
    label.setAttribute("fill", palette.text);
    labelLines.forEach((line, i) => {
      const tspan = document.createElementNS(svgNS, "tspan");
      tspan.setAttribute("x", pos.x);
      if (i > 0) tspan.setAttribute("dy", LABEL_LINE_HEIGHT);
      tspan.textContent = line;
      label.appendChild(tspan);
    });

    const scoreText = document.createElementNS(svgNS, "text");
    scoreText.setAttribute("x", pos.x);
    scoreText.setAttribute("y", labelFirstY + labelLines.length * LABEL_LINE_HEIGHT + 2);
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
   *
   * Node KHÔNG có start_time -> LUÔN hiện ngay (không thể "khoá theo video" một
   * thứ không có mốc thời gian). Quan trọng với lesson nguồn là slide/PDF (AI
   * sinh graph nhưng không có timeline video) — nếu không có dòng này, graph
   * sẽ trống trơn mãi mãi vì mọi node đều thiếu start_time.
   */
  function revealUpTo(currentSec) {
    Object.entries(nodeEls).forEach(([conceptId, { g }]) => {
      const node = nodeById.get(conceptId);
      const revealed = node.start_time == null || currentSec >= node.start_time;
      g.classList.toggle("kg-node--hidden", !revealed);
    });
    edgeEls.forEach(({ path, labelEl, source, target }) => {
      const sourceNode = nodeById.get(source);
      const targetNode = nodeById.get(target);
      const sourceRevealed = !!sourceNode && (sourceNode.start_time == null || currentSec >= sourceNode.start_time);
      const targetRevealed = !!targetNode && (targetNode.start_time == null || currentSec >= targetNode.start_time);
      const revealed = sourceRevealed && targetRevealed;
      path.classList.toggle("kg-edge--hidden", !revealed);
      if (labelEl) labelEl.classList.toggle("kg-edge--hidden", !revealed);
    });
  }

  return { setActiveConcept, updateNodeMastery, onNodeClick, revealUpTo, getActiveConcept: () => activeId };
}

/**
 * Bẻ tên khái niệm thành tối đa `maxLines` dòng, mỗi dòng tối đa `maxCharsPerLine`
 * ký tự, ưu tiên ngắt ở khoảng trắng giữa các từ (không cắt vỡ từ giữa chừng
 * trừ khi 1 từ đơn đã dài hơn cả 1 dòng). Hết chỗ mà vẫn còn nội dung thì thêm
 * "…" vào cuối dòng cuối cùng thay vì để tràn ra ngoài hình tròn.
 */
function wrapNodeLabel(text, maxCharsPerLine = 10, maxLines = 3) {
  const words = String(text).trim().split(/\s+/).filter(Boolean);
  const lines = [];
  let current = "";

  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length <= maxCharsPerLine || !current) {
      current = candidate;
      continue;
    }
    lines.push(current);
    current = word;
    if (lines.length === maxLines) return truncateLastLine(lines, maxCharsPerLine);
  }
  if (current) lines.push(current);

  if (lines.length > maxLines) return truncateLastLine(lines.slice(0, maxLines), maxCharsPerLine);
  // Không thiếu chữ nào, nhưng 1 từ đơn tự nó vẫn có thể dài hơn cả 1 dòng.
  return lines.map(line => (line.length > maxCharsPerLine ? line.slice(0, maxCharsPerLine - 1) + "…" : line));
}

function truncateLastLine(lines, maxCharsPerLine) {
  const last = lines[lines.length - 1] || "";
  const cut = last.length > maxCharsPerLine - 1 ? last.slice(0, maxCharsPerLine - 1) : last;
  lines[lines.length - 1] = cut.replace(/[.,;:\s]+$/, "") + "…";
  return lines;
}
