# Ingestion Audit Report

| Source Type | Existing Tool | Implemented? | Integrated? | Metadata Preserved? | Tested? | Current Status | Main Failure |
|---|---|---|---|---|---|---|---|
| PDF | `pypdf` (`DocumentIngestor.ingest_pdf_file`) | Yes | Yes | Yes (page -> slide) | Yes | PARTIAL | Fails on scanned/image-only PDFs (`chunks_count = 0`). |
| PPTX | `python-pptx` (`DocumentIngestor.ingest_pptx_file`) | Yes | Yes | Yes (slide num) | Yes | READY | Skips slides without text; may alter slide mapping slightly. |
| YouTube | `youtube_transcript_api` (`DocumentIngestor.ingest_youtube_url`) | Yes | Yes | Yes (start_time, end_time) | Yes | READY | Fails if CC/transcripts are unavailable on the video. |
| Local Video | None | No | No | No | No | MISSING | Uploaded video files are not transcribed (`chunks_count = 0`). |
| Text / DOCX | `python-docx` / custom fallback | Yes | Yes | Yes (paragraphs/headings -> slide) | Yes | READY | DOCX slide mapping based on headings can be arbitrary. |

# Lesson Studio Ingestion Audit

Date: 2026-09-18

Audited `adaptive_learning/ingestion.py`, `adaptive_learning/api.py`, `adaptive_learning/models.py`, `adaptive_learning/source_mapper.py`, `adaptive_learning/storage.py`, ingestion tests, and `data/storage.json`. No OCR, Whisper, or other extraction library was installed.

Existing ingestion tests: `eval/test_real_upload.py` and `eval/test_be_modules.py`: **2 passed, 51 existing deprecation warnings**. The full suite currently passes **24 tests**.

Stored-data snapshot: **19 documents**, **54 lessons**, **1,445 chunks**, **1,411 unique chunk IDs**, **34 duplicate chunk IDs**, **1,445 chunks missing `document_id`**, **541 slide/page-bearing chunks**, and **904 timestamp-bearing chunks**. These records include repeated test/upload activity and must not be treated as a clean evaluation corpus.

## Source-type status

| Source Type | Existing Tool | Implemented? | Integrated? | Metadata Preserved? | Tested? | Current Status | Main Failure |
|---|---|---:|---:|---:|---:|---|---|
| PDF | `pypdf.PdfReader` / `DocumentIngestor.ingest_pdf_file` | Yes | Yes via `/adaptive/upload` and remote document flow | Page is preserved as `page` and `slide`; document ID is not copied into stored chunks | Partial | PARTIAL | Scanned/image-only PDFs return `OCR_REQUIRED`; many stored PDF records have zero chunks. |
| PPT/PPTX | `python-pptx.Presentation` / `DocumentIngestor.ingest_pptx_file` | Yes | Yes via upload/remote document flow | 1-based slide number preserved for emitted text chunks | Partial | PARTIAL | Empty/image-only slides are omitted; real PPTX extraction is not directly asserted by tests. |
| YouTube transcript | `youtube-transcript-api` / `DocumentIngestor.ingest_youtube_url` | Yes | Yes via `/adaptive/lessons/video` | `start_time`/`end_time` and lesson ID preserved; document ID missing | Partial | PARTIAL | Captions may be unavailable; duplicate source groups and encoding corruption exist in storage. |
| Local video | None; `LOCAL_VIDEO_EXTENSIONS` are rejected | No | No | N/A | Rejection path only | MISSING | No local transcription; non-YouTube video receives `TRANSCRIPTION_REQUIRED`. |
| Text / DOCX / subtitles | `process_raw_text`, `ingest_docx_file`, `ingest_srt_vtt_file` | Yes | DOCX is upload-integrated; TXT/SRT/VTT are helper-only | DOCX gets synthetic slides; TXT/SRT/VTT preserve lesson/timestamps but IDs/document IDs are incomplete | Partial | PARTIAL | `/adaptive/upload` accepts only PDF/PPTX/DOCX; helper IDs can collide across lessons. |

## Detailed findings

### PDF

`DocumentIngestor.ingest_pdf_file` uses `pypdf.PdfReader` page by page. Each non-empty page becomes a chunk with `slide = page number` and `page = page number`. Empty/image-only PDFs raise `OCR_REQUIRED` instead of silently succeeding. `pdf_is_likely_scanned` also exists, but the upload path primarily classifies the extraction result.

Successful stored examples: `doc_07` / `lesson_20` with 421 chunks and `doc_08` / `lesson_21` with 29 chunks. Empty examples include `doc_04`, `doc_05`, `doc_09` through `doc_18`; `doc_19` / `lesson_54` explicitly has `INGESTION_FAILED` and `OCR_REQUIRED`. The zero-chunk historical records do not all retain an error code.

Status: **PARTIAL**. Text PDFs work, but scanned PDFs need an explicit OCR decision and the stored corpus contains many failed records.

### PPT/PPTX

`DocumentIngestor.ingest_pptx_file` uses `python-pptx.Presentation`, iterates presentation order, and emits `slide = idx + 1`. Text-bearing shapes are concatenated. Image-only or empty slides are omitted, so emitted chunk count may be lower than physical slide count and `total_slides` is derived from emitted chunks.

Successful stored examples: `doc_03` / `lesson_09` and `doc_06` / `lesson_19`, each with 45 chunks. Existing tests verify structured slide metadata but do not directly assert extraction from a real PPTX.

Status: **PARTIAL**.

### YouTube transcript

`DocumentIngestor.ingest_youtube_url` uses `youtube-transcript-api`, requests Vietnamese/English captions, and groups entries into approximately 30-second chunks with rounded `start_time` and `end_time`. The route is `_create_video_lesson` at `POST /adaptive/lessons/video`.

Successful example: `lesson_52` with `source_key = youtube:PTXkJbkGtUw` and `READY` status. Timed chunks also exist for `lesson_02`, `lesson_03`, `lesson_06`, `lesson_07`, `lesson_10`, `lesson_12`, `lesson_15`, `lesson_16`, `lesson_22`, `lesson_25`, `lesson_28`, `lesson_31`, and `lesson_34`.

Failed/partial example: `doc_02` is a video record with zero chunks. Historical duplicate content was found for `lesson_06`/`lesson_15` and `lesson_03`/`lesson_10`. Current API deduplication does exist: canonical YouTube IDs and file hashes become `source_key` values, but older records were not cleaned. Some transcript text contains mojibake markers such as `Ã` or `�`.

Status: **PARTIAL**.

### Local video

No local transcription implementation exists. `LOCAL_VIDEO_EXTENSIONS` is defined, but `_handle_document_upload` rejects video/audio extensions and returns a message directing users to YouTube or a transcript file. Non-YouTube video URLs are saved with `TRANSCRIPTION_REQUIRED` and no chunks.

Status: **MISSING**. No Whisper or other transcription dependency should be installed as part of this audit.

### Text, DOCX, subtitles, and chunking

- `process_raw_text` splits plain text by blank lines and assigns synthetic `slide=1`.
- `ingest_docx_file` groups paragraphs/headings and assigns synthetic sequential slides.
- `ingest_transcript_json` preserves supplied timestamps.
- `ingest_srt_vtt_file` parses subtitle time ranges and preserves timestamps.
- The public upload route accepts PDF, PPTX, and DOCX only; TXT/SRT/VTT are helper paths.

Chunk IDs are only partly globally safe. PDF/PPTX/YouTube use `_chunk_id(prefix, lesson_id, index)`, but helper paths emit IDs such as `chunk_slide_001`, `chunk_tr_001`, `chunk_sub_001`, and `chunk_txt_001` without lesson scope. Storage confirms 34 duplicate IDs. All 1,445 stored chunks also lack `document_id`, so document-level traceability is currently unavailable.

Status: **PARTIAL**.

### Source mapping

`Chunk` preserves `lesson_id`, `slide`, `page`, `start_time`, and `end_time`. `SourceMapper` provides slide/time-to-concept lookups, but defaults to `MOCK_SOURCE_MAPPING` unless real mappings are supplied. API endpoints expose stored slide/transcript content and `_persist_chunks_and_concepts` persists lesson-scoped concept mappings.

The mapping is not fully reliable for real evaluation because stored chunks lack `document_id`, the AI graph endpoint reconstructs document identity as the lesson ID, and the mapper has mock-default behavior.

Status: **PARTIAL**.

## Specific audit answers

- **PDFs with `chunks_count = 0`:** `doc_04`, `doc_05`, `doc_09` through `doc_18`; explicit OCR failure is `doc_19` / `lesson_54`.
- **Scanned/image-only PDFs:** detected as `OCR_REQUIRED`; no OCR fallback exists.
- **PPTX slide numbering:** 1-based numbering is preserved for emitted text slides; empty/image-only slides are omitted.
- **YouTube timestamps:** preserved in generated 30-second chunks when captions are available.
- **Local video with no chunks:** no transcription path; rejected with `TRANSCRIPTION_REQUIRED` or stored without chunks for non-YouTube URLs.
- **Duplicate source ingestion:** current API has file-hash and canonical YouTube source-key checks, but historical duplicates remain in storage.
- **Globally safe chunk IDs:** not guaranteed across all helper ingestion paths; 34 duplicate IDs are present.

## What works

Text-bearing PDF extraction, PPTX text extraction, YouTube caption extraction, DOCX paragraph ingestion, structured slide/transcript helpers, page/slide/timestamp preservation, and explicit scanned-PDF classification. Existing ingestion tests pass.

## What is partial or missing

PDF scanned-source recovery, PPTX physical-slide accounting, YouTube caption/encoding reliability, first-class TXT/SRT/VTT routes, real source mapping, document identity propagation, and global chunk IDs are partial. Local video/audio transcription is missing.

## Fix before real-data evaluation

1. Repair or exclude zero-chunk records and retain failure codes.
2. Preserve `document_id` and `source_group` on every stored chunk.
3. Make every helper chunk ID globally safe, preferably including document and lesson ID.
4. Deduplicate by canonical source group; do not split `lesson_06`/`lesson_15` or `lesson_03`/`lesson_10` across evaluation sets.
5. Repair transcript/PDF encoding and verify PPTX physical slide counts.
6. Add focused tests for real PDF extraction, scanned PDF classification, PPTX numbering, YouTube timestamps, duplicate sources, and metadata persistence.
7. Only then select clean lessons for human-labeled evaluation. Do not install OCR or transcription tooling before these contracts are fixed.

## Final status

**PDF:** PARTIAL. Text PDFs work with page metadata; scanned PDFs are explicitly rejected as `OCR_REQUIRED`.

**PPTX:** PARTIAL. Text extraction and slide numbering exist, but empty-slide behavior and real extraction are under-tested.

**YouTube:** PARTIAL. Transcript/timestamp extraction works when captions exist; duplicate, encoding, and document-ID issues remain.

**Local video:** MISSING. No transcription implementation.

**Text:** PARTIAL. Text, DOCX, SRT, VTT, and structured helpers exist, but only some are public ingestion routes and metadata/ID contracts are inconsistent.

**Bottom line:** the repository has a functioning text-based ingestion core, but it is not ready for real-data AI evaluation until source identity, chunk-ID integrity, duplicate/failed corpus cleanup, encoding, and source mapping are repaired.

### Observations on Specific Concerns
- **PDFs with chunks_count = 0:** Observed in `storage.json` (`doc_04`, `doc_05`, `doc_09`, `doc_10`, `doc_11`, `doc_12`, `doc_13`, `doc_14`, `doc_15`). This happens because `pypdf.extract_text()` fails on scanned or image-heavy PDFs with no embedded text layer.
- **PPTX slide numbering:** Preserved correctly as `slide = idx + 1`, however, empty/image-only slides are skipped which means the chunk indices won't include them, but the ones preserved will retain their correct original slide number.
- **YouTube transcript timestamps:** Correctly preserved into 30-second windows with `start_time` and `end_time`.
- **Local video files with no chunks:** Confirmed in `storage.json` (e.g., `doc_02` "video AI.mp4"). The API `/adaptive/lessons/video` only handles YouTube URLs and skips extraction for other video sources.
- **Duplicate lesson/source ingestion:** Duplicate URL/file ingestion is completely unchecked. `storage.json` shows multiple copies of the same YouTube video (`PTXkJbkGtUw`) ingested as `lesson_10`, `lesson_12`, `lesson_16`, `lesson_22`, `lesson_25`, `lesson_28`, etc. There is no deduplication mechanism.
- **Globally safe chunk IDs:** Yes, the implementation `_chunk_id(prefix, lesson_id, idx)` guarantees chunk IDs are globally safe across lessons.

### INGESTION STATUS

PDF: PARTIAL
PPTX: READY
YouTube: READY
Local video: MISSING
Text: READY

What already works: Text extraction from digital PDFs, PPTXs, DOCX, and Text documents via API upload. YouTube URLs pull caption data and timestamps successfully.
What is partial: PDF ingestion; it completely fails on scanned or image-only PDFs.
What is missing: Local video/audio file transcription (no OCR or Whisper capabilities).
What should be fixed before real-data evaluation:
1. Deduplication of uploaded sources (prevent re-ingesting the exact same YouTube URL or file and flooding the storage).
2. Add OCR/Image fallback for scanned PDFs (or clearly reject them instead of succeeding with 0 chunks).
3. Implement a transcription mechanism for local video files (or reject them cleanly, as currently they silently process with 0 chunks).

