import os
import re
import json
import uuid
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from .models import (
    RecommendationResponse,
    StudentAnswer,
    Chunk,
    GraphResponse,
    VideoLinkRequest,
    SlideLinkRequest,
)
from .mastery import compute_mastery, compute_mastery_state
from .graph import find_weak_prerequisite
from .ingestion import DocumentIngestor
from .storage import db_storage
from ai.pipeline import build_graph as ai_build_graph

adaptive_router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Upload chỉ nhận tài liệu / slide — KHÔNG nhận video file
ALLOWED_DOC_EXTENSIONS = {".pdf", ".pptx", ".docx"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
PLACEHOLDER_STRINGS = {"", "string", "null", "none", "undefined"}


def get_student_mastery_scores(student_id: str) -> Dict[str, Optional[float]]:
    """Helper to compute mastery for all concepts for a given student from persistent DB."""
    attempts = db_storage.get_student_attempts(student_id)
    concept_attempts: Dict[str, List[Dict[str, Any]]] = {}
    for a in attempts:
        cid = a["concept_id"]
        concept_attempts.setdefault(cid, []).append(a)

    mastery_scores: Dict[str, Optional[float]] = {}
    concepts = db_storage.data.get("concepts", {})
    for cid in concepts.keys():
        if cid in concept_attempts:
            mastery_scores[cid] = compute_mastery(concept_attempts[cid])
        else:
            mastery_scores[cid] = None
    return mastery_scores


def _clean_optional_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned.lower() in PLACEHOLDER_STRINGS:
        return None
    return cleaned


def _is_valid_http_url(url: Optional[str]) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def _is_youtube_url(url: Optional[str]) -> bool:
    if not url:
        return False
    return "youtube.com" in url or "youtu.be" in url


def _public_upload_path(filename: str) -> str:
    """URL path FE có thể gọi qua StaticFiles mount /uploads."""
    return f"/uploads/{filename}"


def _safe_filename(original: str) -> str:
    base = os.path.basename(original or "document")
    base = re.sub(r"[^\w.\-]+", "_", base, flags=re.UNICODE)
    if not base or base in {".", ".."}:
        base = f"document_{uuid.uuid4().hex[:8]}"
    name, ext = os.path.splitext(base)
    return f"{name}_{uuid.uuid4().hex[:8]}{ext.lower()}"


def _persist_chunks_and_concepts(chunks: List[Chunk], lesson_id: str) -> float:
    """Lưu chunks (thay thế theo lesson), extract concepts, trả về duration_seconds."""
    duration_seconds = 0.0
    if not chunks:
        return duration_seconds

    # Tránh trùng chunk khi upload/link lại cùng lesson
    db_storage.replace_chunks_for_lesson(lesson_id, [c.dict() for c in chunks])

    extracted = DocumentIngestor.extract_clean_concepts_from_chunks(chunks)
    for cid, cinfo in extracted.get("concepts", {}).items():
        cinfo = dict(cinfo)
        cinfo["lesson_id"] = lesson_id
        db_storage.data["concepts"][cid] = cinfo
    for cid, sinfo in extracted.get("source_mappings", {}).items():
        sinfo = dict(sinfo)
        sinfo["lesson_id"] = lesson_id
        db_storage.data["source_mappings"][cid] = sinfo

    for c in chunks:
        if c.end_time is not None and c.end_time > duration_seconds:
            duration_seconds = c.end_time

    return round(duration_seconds, 2)


def _ingest_uploaded_doc(file_path: str, file_ext: str, lesson_id: str) -> List[Chunk]:
    if file_ext == ".pdf":
        return DocumentIngestor.ingest_pdf_file(file_path, lesson_id=lesson_id)
    if file_ext == ".pptx":
        return DocumentIngestor.ingest_pptx_file(file_path, lesson_id=lesson_id)
    if file_ext == ".docx":
        return DocumentIngestor.ingest_docx_file(file_path, lesson_id=lesson_id)
    return []


def _slide_url_ingest_hint(slide_url: str) -> str:
    """Giải thích vì sao slide_url không bóc tách được."""
    host = (urlparse(slide_url).netloc or "").lower()
    path = (urlparse(slide_url).path or "").lower()

    if "scribd.com" in host:
        return (
            "Link Scribd chỉ là trang xem web (cần đăng nhập/trả phí), backend không tải được file. "
            "Hãy tải PDF/PPTX/DOCX về máy rồi upload qua POST /adaptive/upload."
        )
    if "slideshare.net" in host:
        return (
            "Link SlideShare không phải file tải trực tiếp. "
            "Hãy tải PDF về máy rồi upload qua POST /adaptive/upload."
        )
    if "docs.google.com" in host or "drive.google.com" in host:
        return (
            "Google Docs/Slides/Drive chưa export được (thường do file private). "
            "Bật chia sẻ 'Anyone with the link can view', hoặc tải .pdf/.pptx/.docx rồi upload."
        )
    if path.endswith((".pdf", ".pptx", ".docx")):
        return (
            "Link file không tải được (404/chặn hotlink). "
            "Thử upload file trực tiếp qua POST /adaptive/upload."
        )
    return (
        "slide_url đã lưu nhưng chưa bóc tách được. "
        "Hỗ trợ: (1) link .pdf/.pptx/.docx tải trực tiếp, "
        "(2) Google Docs / Slides / Drive public. "
        "Cách chắc nhất: upload file qua POST /adaptive/upload."
    )


def _ingest_remote_slide_url(slide_url: str, lesson_id: str) -> List[Chunk]:
    """
    Ingest khi tải được file thật (PDF/PPTX/DOCX) hoặc Google Docs/Slides/Drive public.
    Scribd / SlideShare / viewer HTML → không ingest.
    """
    if not _is_valid_http_url(slide_url):
        return []

    host = (urlparse(slide_url).netloc or "").lower()
    if any(h in host for h in ("scribd.com", "slideshare.net", "canva.com", "prezi.com")):
        return []

    parsed = urlparse(slide_url)
    path_lower = (parsed.path or "").lower()
    ext = os.path.splitext(path_lower)[1]
    lower = slide_url.lower()

    should_try = (
        ext in ALLOWED_DOC_EXTENSIONS
        or "docs.google.com/presentation" in lower
        or "docs.google.com/document" in lower
        or "drive.google.com" in lower
    )
    if not should_try:
        return []

    try:
        return DocumentIngestor.ingest_remote_document(
            slide_url, lesson_id=lesson_id, upload_dir=UPLOAD_DIR
        )
    except Exception as e:
        print(f"[API] Remote slide/doc ingest skipped: {e}")
        return []


def _merge_lesson(
    lesson_id: str,
    title: str,
    *,
    source_type: str,
    video_url: Optional[str] = None,
    slide_url: Optional[str] = None,
    file_path: Optional[str] = None,
    total_slides: int = 0,
    duration_seconds: float = 0,
) -> Dict[str, Any]:
    """Mỗi lesson chỉ giữ ĐÚNG 1 nguồn: video | slide | document."""
    existing = db_storage.get_lesson(lesson_id) or {}
    lesson_record = {
        "lesson_id": lesson_id,
        "title": title or existing.get("title") or "Bài giảng mới",
        "source_type": source_type,
        "video_url": video_url if source_type == "video" else None,
        "slide_url": slide_url if source_type == "slide" else None,
        "file_path": file_path if source_type == "document" else None,
        "total_slides": total_slides if source_type in ("slide", "document") else 0,
        "duration_seconds": duration_seconds if source_type == "video" else 0,
    }
    db_storage.save_lesson(lesson_record)
    return lesson_record


# ============================================================================
# 1. INGESTION — ĐÚNG 1 TRONG 3: video | slide | document
# ============================================================================

async def _handle_document_upload(
    file: UploadFile,
    title: Optional[str] = None,
):
    """Upload CHỈ file document (.pdf / .pptx)."""
    title = _clean_optional_str(title)

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Cần upload file .pdf / .pptx / .docx.",
        )

    filename = file.filename or "document"
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext in VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Không upload video. Dùng POST /adaptive/lessons/video với video_url.",
        )
    if file_ext not in ALLOWED_DOC_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ chấp nhận .pdf / .pptx / .docx. Nhận được: {file_ext or '(không có đuôi)'}",
        )

    target_lesson_id = db_storage.get_next_lesson_id()
    file_title = title or os.path.splitext(os.path.basename(filename))[0]
    safe_name = _safe_filename(filename)
    disk_path = os.path.join(UPLOAD_DIR, safe_name)
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File upload rỗng.")

    with open(disk_path, "wb") as f:
        f.write(contents)

    public_file_path = _public_upload_path(safe_name)
    if file_ext == ".pdf":
        doc_type = "pdf"
    elif file_ext == ".pptx":
        doc_type = "pptx"
    else:
        doc_type = "docx"

    try:
        chunks = _ingest_uploaded_doc(disk_path, file_ext, target_lesson_id)
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không đọc được file {file_ext}: {e}")

    _persist_chunks_and_concepts(chunks, target_lesson_id)
    slide_numbers = [c.slide for c in chunks if c.slide is not None]
    total_slides = max(slide_numbers) if slide_numbers else 0

    lesson_record = _merge_lesson(
        target_lesson_id,
        file_title,
        source_type="document",
        file_path=public_file_path,
        total_slides=total_slides,
        duration_seconds=0,
    )

    doc_id = db_storage.get_next_document_id()
    doc_record = {
        "document_id": doc_id,
        "title": file_title,
        "file_type": doc_type,
        "file_path": public_file_path,
        "lesson_id": target_lesson_id,
        "chunks_count": len(chunks),
    }
    db_storage.save_document(doc_record)
    db_storage.save()

    return {
        "status": "success",
        "source_type": "document",
        "message": f"Đã nạp document {target_lesson_id} thành công!",
        "lesson": lesson_record,
        "document": doc_record,
        "parsed_slides_count": total_slides,
        "parsed_chunks_count": len(chunks),
        "warnings": [],
    }


def _create_video_lesson(video_url: str, title: Optional[str] = None, lesson_id: Optional[str] = None):
    video_url = _clean_optional_str(video_url)
    title = _clean_optional_str(title)
    lesson_id_input = _clean_optional_str(lesson_id)

    if not video_url or not _is_valid_http_url(video_url):
        raise HTTPException(status_code=400, detail="video_url không hợp lệ (cần http/https).")

    lid = lesson_id_input or db_storage.get_next_lesson_id()
    resolved_title = title or "Bài giảng Video"
    chunks: List[Chunk] = []
    warnings: List[str] = []

    if _is_youtube_url(video_url):
        yt_chunks = DocumentIngestor.ingest_youtube_url(video_url, lesson_id=lid)
        if yt_chunks:
            chunks.extend(yt_chunks)
        else:
            warnings.append("Không lấy được phụ đề YouTube (video có thể không có transcript).")
    else:
        warnings.append("video_url không phải YouTube — đã lưu link, không có transcript tự động.")

    duration_seconds = _persist_chunks_and_concepts(chunks, lid) if chunks else 0.0
    lesson_data = _merge_lesson(
        lid,
        resolved_title,
        source_type="video",
        video_url=video_url,
        duration_seconds=duration_seconds,
    )
    db_storage.save()

    return {
        "status": "success",
        "source_type": "video",
        "message": "Đã lưu link VIDEO thành công!",
        "lesson": lesson_data,
        "youtube_transcript_fetched_chunks": len(chunks),
        "parsed_slides_count": 0,
        "parsed_chunks_count": len(chunks),
        "warnings": warnings,
    }


def _create_slide_lesson(slide_url: str, title: Optional[str] = None, lesson_id: Optional[str] = None):
    slide_url = _clean_optional_str(slide_url)
    title = _clean_optional_str(title)
    lesson_id_input = _clean_optional_str(lesson_id)

    if not slide_url or not _is_valid_http_url(slide_url):
        raise HTTPException(status_code=400, detail="slide_url không hợp lệ (cần http/https).")

    lid = lesson_id_input or db_storage.get_next_lesson_id()
    resolved_title = title or "Tài liệu Slide"
    warnings: List[str] = []

    chunks = _ingest_remote_slide_url(slide_url, lid)
    if not chunks:
        warnings.append(_slide_url_ingest_hint(slide_url))

    if chunks:
        _persist_chunks_and_concepts(chunks, lid)
    slide_numbers = [c.slide for c in chunks if c.slide is not None]
    total_slides = max(slide_numbers) if slide_numbers else 0

    lesson_data = _merge_lesson(
        lid,
        resolved_title,
        source_type="slide",
        slide_url=slide_url,
        total_slides=total_slides,
    )
    db_storage.save()

    return {
        "status": "success",
        "source_type": "slide",
        "message": "Đã lưu link SLIDE thành công!",
        "lesson": lesson_data,
        "youtube_transcript_fetched_chunks": 0,
        "parsed_slides_count": total_slides,
        "parsed_chunks_count": len(chunks),
        "warnings": warnings,
    }


@adaptive_router.post("/lessons/video")
def create_lesson_from_video(payload: VideoLinkRequest):
    """Cách 1/3 — Body chỉ có video_url."""
    return _create_video_lesson(payload.video_url)


@adaptive_router.post("/lessons/slide")
def create_lesson_from_slide(payload: SlideLinkRequest):
    """Cách 2/3 — Body chỉ có slide_url."""
    return _create_slide_lesson(payload.slide_url)


@adaptive_router.post("/upload")
async def upload_document(
    file: UploadFile = File(..., description="File .pdf / .pptx / .docx"),
):
    """
    Cách 3/3 — Upload DOCUMENT (.pdf / .pptx / .docx).
    Request body chỉ cần 1 field: file.
    """
    return await _handle_document_upload(file)


# ============================================================================
# 2. RETRIEVAL ENDPOINTS
# ============================================================================

@adaptive_router.get("/lessons")
def get_all_lessons():
    """GET /adaptive/lessons — danh sách tất cả bài giảng."""
    lessons = db_storage.get_all_lessons()
    return {"count": len(lessons), "lessons": lessons}


@adaptive_router.get("/lessons/{lesson_id}")
def get_lesson_detail(lesson_id: str):
    """
    GET /adaptive/lessons/{lesson_id}
    Chi tiết bài giảng + slides + transcript + concepts (scoped theo lesson).
    """
    lesson = db_storage.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bài giảng với ID: {lesson_id}")

    slides = db_storage.get_slides_by_lesson(lesson_id)
    transcript = db_storage.get_transcript_by_lesson(lesson_id)

    result = dict(lesson)
    result["slides_count"] = len(slides)
    result["slides"] = slides
    result["transcript_chunks_count"] = len(transcript)
    result["transcript"] = transcript
    result["concepts"] = db_storage.get_concepts_by_lesson(lesson_id)
    return result


@adaptive_router.get("/lessons/{lesson_id}/slides/{slide_number}")
def get_slide_content(lesson_id: str, slide_number: int):
    """GET /adaptive/lessons/{lesson_id}/slides/{slide_number}"""
    if not db_storage.get_lesson(lesson_id):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bài giảng với ID: {lesson_id}")

    slides = db_storage.get_slides_by_lesson(lesson_id)
    matched = [s for s in slides if s.get("slide") == slide_number]
    if not matched:
        return {
            "lesson_id": lesson_id,
            "slide": slide_number,
            "found": False,
            "text": "Không tìm thấy nội dung văn bản cho trang Slide này.",
        }
    return {
        "lesson_id": lesson_id,
        "slide": slide_number,
        "found": True,
        "text": matched[0].get("text"),
    }


@adaptive_router.get("/documents")
def get_all_documents():
    """GET /adaptive/documents — danh sách file doc/slide đã upload."""
    docs = db_storage.get_all_documents()
    return {"count": len(docs), "documents": docs}


# ============================================================================
# 3. KNOWLEDGE GRAPH & SOURCE MAPPER
# ============================================================================

@adaptive_router.get("/knowledge-graph/{lesson_id}", response_model=GraphResponse)
def get_knowledge_graph(lesson_id: str):
    """
    GET /adaptive/knowledge-graph/{lesson_id}
    Nodes & edges scoped theo lesson (không trả toàn bộ global mock nếu lesson có concept riêng).
    """
    if not db_storage.get_lesson(lesson_id):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bài giảng với ID: {lesson_id}")

    lesson_concepts = db_storage.get_concepts_by_lesson(lesson_id)
    concept_ids = {c.get("concept_id") for c in lesson_concepts if c.get("concept_id")}

    concepts = db_storage.data.get("concepts", {})
    source_mappings = db_storage.data.get("source_mappings", {})
    prerequisites = db_storage.data.get("prerequisites", {})

    nodes = []
    for cid in concept_ids:
        info = concepts.get(cid, {})
        src = source_mappings.get(cid, {})
        nodes.append({
            "id": cid,
            "label": info.get("name"),
            "slide": src.get("slide"),
            "start_time": src.get("start_time"),
            "end_time": src.get("end_time"),
        })

    edges = []
    for target_id, prereqs in prerequisites.items():
        if target_id not in concept_ids:
            continue
        for src_id in prereqs:
            if src_id in concept_ids:
                edges.append({
                    "from": src_id,
                    "to": target_id,
                    "type": "prerequisite",
                })

    return GraphResponse(nodes=nodes, edges=edges)


@adaptive_router.post("/lessons/{lesson_id}/generate-graph")
def generate_graph_from_ai(lesson_id: str):
    """
    POST /adaptive/lessons/{lesson_id}/generate-graph
    Chạy module ai/ (trích xuất concept/quan hệ theo luật, có căn cứ nguồn) trên
    TOÀN BỘ chunk đã ingest của lesson này, rồi GHI ĐÈ kết quả vào storage —
    khác với GET /knowledge-graph/{lesson_id} (chỉ ĐỌC dữ liệu đã có sẵn).

    Lưu ý: ai/ hiện nhận diện theo danh sách từ khoá cố định (chủ yếu thuật
    ngữ ML tiếng Anh: gradient descent, loss function, regression...) — lesson
    không có chunk nào chứa các từ khoá này sẽ ra graph rỗng, không phải lỗi.
    """
    if not db_storage.get_lesson(lesson_id):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bài giảng với ID: {lesson_id}")

    raw_chunks = db_storage.get_chunks_by_lesson(lesson_id)
    if not raw_chunks:
        raise HTTPException(
            status_code=400,
            detail=f"Lesson '{lesson_id}' chưa có chunk nào (chưa ingest video/slide/document) — không có gì để phân tích."
        )

    # Chunk lưu dạng phẳng (chunk_id/text/slide/start_time/end_time) -> ai.pipeline
    # cần gói slide/start_time/end_time vào trong 1 field "source".
    ai_chunks = [
        {
            "chunk_id": c.get("chunk_id"),
            "document_id": lesson_id,
            "text": c.get("text"),
            "source": {
                "slide": c.get("slide"),
                "start_time": c.get("start_time"),
                "end_time": c.get("end_time"),
            },
        }
        for c in raw_chunks
    ]

    graph = ai_build_graph(ai_chunks, lesson_id=lesson_id)

    # QUAN TRỌNG: id do ai.pipeline sinh ra là id CANONICAL DÙNG CHUNG (VD "gradient_descent"
    # luôn cùng 1 id dù trích từ lesson nào) — nếu ghi thẳng id đó vào storage (dict phẳng,
    # khoá toàn cục), 2 lesson khác nhau cùng nhắc tới "Gradient Descent" sẽ ĐÈ LÊN NHAU, lesson
    # sinh sau "cướp" mất node của lesson sinh trước. Phải gắn tiền tố lesson_id vào id khi lưu
    # (đúng cách Tài đã làm với các concept "c_lesson_XX_..." có sẵn) để mỗi lesson có bộ node
    # độc lập, không đụng lesson khác dù trùng khái niệm.
    def scoped_id(raw_id: str) -> str:
        return f"ai_{lesson_id}_{raw_id}"

    # Ghi kết quả vào đúng 3 chỗ mà GET /knowledge-graph/{lesson_id} đang đọc.
    for node in graph["nodes"]:
        cid = scoped_id(node["id"])
        db_storage.data["concepts"][cid] = {
            "name": node["label"],
            "description": node.get("description", ""),
            "lesson_id": lesson_id,
        }
        first_source = node["sources"][0] if node.get("sources") else {}
        db_storage.data["source_mappings"][cid] = {
            "slide": first_source.get("slide"),
            "start_time": first_source.get("start_time"),
            "end_time": first_source.get("end_time"),
            "lesson_id": lesson_id,
        }

    # Schema hiện tại chỉ lưu quan hệ "prerequisite" (không có chỗ cho used_for/type_of/part_of...)
    # nên chỉ giữ đúng loại "prerequisite_of", các loại quan hệ khác AI trả về sẽ không được lưu.
    for edge in graph["edges"]:
        if edge.get("relation") != "prerequisite_of":
            continue
        target_id = scoped_id(edge["target"])
        source_id = scoped_id(edge["source"])
        db_storage.data["prerequisites"].setdefault(target_id, [])
        if source_id not in db_storage.data["prerequisites"][target_id]:
            db_storage.data["prerequisites"][target_id].append(source_id)

    db_storage.save()

    return {
        "lesson_id": lesson_id,
        "concepts_generated": len(graph["nodes"]),
        "edges_generated": len([e for e in graph["edges"] if e.get("relation") == "prerequisite_of"]),
        "edges_dropped_unsupported_relation": len([e for e in graph["edges"] if e.get("relation") != "prerequisite_of"]),
        "graph": graph,
    }


@adaptive_router.get("/concepts/by-slide/{slide_number}")
def get_concepts_by_slide(slide_number: int, lesson_id: Optional[str] = None):
    """
    GET /adaptive/concepts/by-slide/{slide_number}?lesson_id=lesson_02
    Ánh xạ slide ➔ concepts (nên truyền lesson_id để lọc đúng bài).
    """
    source_mappings = db_storage.data.get("source_mappings", {})
    concepts = db_storage.data.get("concepts", {})

    matched_concepts = []
    for cid, src in source_mappings.items():
        if src.get("slide") != slide_number:
            continue
        if lesson_id:
            concept_lesson = src.get("lesson_id") or concepts.get(cid, {}).get("lesson_id")
            if concept_lesson and concept_lesson != lesson_id:
                continue
            # Nếu mapping không có lesson_id, chỉ lấy concept thuộc lesson
            if not concept_lesson:
                lesson_cids = {c.get("concept_id") for c in db_storage.get_concepts_by_lesson(lesson_id)}
                if cid not in lesson_cids:
                    continue

        concept_info = concepts.get(cid, {})
        matched_concepts.append({
            "concept_id": cid,
            "name": concept_info.get("name"),
            "description": concept_info.get("description"),
            "slide": slide_number,
        })

    return {"slide": slide_number, "lesson_id": lesson_id, "concepts": matched_concepts}


@adaptive_router.get("/concepts/by-time/{timestamp_seconds}")
def get_concepts_by_time(timestamp_seconds: float, lesson_id: Optional[str] = None):
    """
    GET /adaptive/concepts/by-time/{timestamp_seconds}?lesson_id=lesson_02
    Ánh xạ giây video ➔ concept.
    """
    source_mappings = db_storage.data.get("source_mappings", {})
    concepts = db_storage.data.get("concepts", {})

    candidates = []
    for cid, src in source_mappings.items():
        st = src.get("start_time")
        et = src.get("end_time")
        if st is None or et is None:
            continue
        if not (st <= timestamp_seconds <= et):
            continue
        if lesson_id:
            concept_lesson = src.get("lesson_id") or concepts.get(cid, {}).get("lesson_id")
            if concept_lesson and concept_lesson != lesson_id:
                continue
            if not concept_lesson:
                lesson_cids = {c.get("concept_id") for c in db_storage.get_concepts_by_lesson(lesson_id)}
                if cid not in lesson_cids:
                    continue
        candidates.append((cid, src))

    if not candidates:
        return {
            "timestamp": timestamp_seconds,
            "lesson_id": lesson_id,
            "concept": None,
            "message": "No concept mapped to this timestamp",
        }

    cid, src = candidates[0]
    concept_info = concepts.get(cid, {})
    return {
        "timestamp": timestamp_seconds,
        "lesson_id": lesson_id,
        "concept": {
            "concept_id": cid,
            "name": concept_info.get("name"),
            "start_time": src.get("start_time"),
            "end_time": src.get("end_time"),
        },
    }


# ============================================================================
# 4. QUIZ & ADAPTIVE LEARNING
# ============================================================================

@adaptive_router.post("/quiz/answer")
def submit_quiz_answer(answer: StudentAnswer, student_id: Optional[str] = "student_01"):
    """POST /adaptive/quiz/answer — nộp quiz, cập nhật mastery."""
    target_student_id = student_id if (student_id and student_id.strip()) else "student_01"
    target_quiz_id = answer.quiz_id if (answer.quiz_id and answer.quiz_id.strip()) else db_storage.get_next_quiz_id()

    attempt = {
        "quiz_id": target_quiz_id,
        "concept_id": answer.concept_id,
        "is_correct": answer.is_correct,
        "difficulty": answer.difficulty,
    }
    db_storage.add_student_attempt(target_student_id, attempt)

    updated_scores = get_student_mastery_scores(target_student_id)
    new_mastery = updated_scores.get(answer.concept_id)
    state = compute_mastery_state(new_mastery, is_current=True)

    return {
        "student_id": target_student_id,
        "quiz_id": target_quiz_id,
        "concept_id": answer.concept_id,
        "new_mastery": new_mastery,
        "mastery_state": state,
        "status": "updated",
    }


@adaptive_router.get("/recommendation/{student_id}", response_model=RecommendationResponse)
def get_recommendation(student_id: str, current_concept_id: str = "c6"):
    """GET /adaptive/recommendation/{student_id} — gợi ý ôn tập theo BFS."""
    mastery_scores = get_student_mastery_scores(student_id)
    current_mastery = mastery_scores.get(current_concept_id)

    concepts = db_storage.data.get("concepts", {})
    prerequisites = db_storage.data.get("prerequisites", {})
    source_mappings = db_storage.data.get("source_mappings", {})

    if current_mastery is not None and current_mastery >= 0.5:
        return RecommendationResponse(
            weak_concept="",
            recommended_concept="",
            reason="Student has mastered the current concept.",
            source={},
        )

    recommended_cid = find_weak_prerequisite(prerequisites, mastery_scores, current_concept_id)

    if recommended_cid == current_concept_id:
        reason = "No prerequisite — review this concept directly"
    else:
        reason = "Weak prerequisite"

    source = source_mappings.get(recommended_cid, {})
    weak_concept_name = concepts.get(current_concept_id, {}).get("name", "Unknown")
    recommended_concept_name = concepts.get(recommended_cid, {}).get("name", "Unknown")

    return RecommendationResponse(
        weak_concept=weak_concept_name,
        recommended_concept=recommended_concept_name,
        reason=reason,
        source=source,
    )


@adaptive_router.get("/mastery/{student_id}")
def get_mastery_summary(student_id: str):
    """GET /adaptive/mastery/{student_id}"""
    scores = get_student_mastery_scores(student_id)
    concepts = db_storage.data.get("concepts", {})

    breakdown = {}
    for cid, score in scores.items():
        state = compute_mastery_state(score)
        breakdown[cid] = {
            "name": concepts.get(cid, {}).get("name"),
            "score": score,
            "state": state,
        }
    return {"student_id": student_id, "mastery_summary": breakdown}
