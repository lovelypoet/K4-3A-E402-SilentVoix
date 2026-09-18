# Real-data readiness

| Area | Status |
|---|---|
| PDF digital | READY for the five new digital PDFs |
| PDF scanned | OCR_REQUIRED |
| PPTX | PARTIAL |
| YouTube | PARTIAL |
| Local video | READY for the two supplied MP4 files; FFmpeg is not on PATH but faster-whisper/AV decoded them |
| Text/DOCX | PARTIAL |
| Deduplication | PARTIAL; new exact-file path is SHA-256 based |
| document_id propagation | READY for newly processed records |
| Real-eval lessons available | 7 selected candidates: 5 PDFs and 2 videos |

## Blockers

1. Human-verify source/document IDs and annotate concepts, relations, grounding, and quiz decisions.
2. Clean or exclude historical duplicate, corrupt, zero-chunk, and legacy records.
3. Install FFmpeg if broader media-format support is required beyond the supplied MP4 files.
