# Ingestion audit

## Current status

| Source | Status | Evidence |
|---|---|---|
| Digital PDF | READY for the five new PDFs | `new_files_processing.md` |
| Scanned PDF | OCR_REQUIRED when no meaningful text is extracted | Existing `ingest_pdf_file` behavior |
| PPTX | PARTIAL | Existing audit: text slides work; image-only slides are not extracted |
| YouTube | PARTIAL | Transcript/timestamps work when captions are available |
| Local video | PARTIAL | Registration and ASR path added; runtime dependency is not installed |
| DOCX/text/subtitles | PARTIAL | Existing helper and upload paths remain available |

New records use SHA-256 source identity, atomic storage writes, and explicit non-READY statuses for zero-chunk sources.
