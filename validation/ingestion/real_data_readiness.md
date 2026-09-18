# Real-data readiness

| Area | Status |
|---|---|
| PDF digital | READY for the five new digital PDFs |
| PDF scanned | OCR_REQUIRED |
| PPTX | PARTIAL |
| YouTube | PARTIAL |
| Local video | PARTIAL; ASR dependency unavailable |
| Text/DOCX | PARTIAL |
| Deduplication | PARTIAL; new exact-file path is SHA-256 based |
| document_id propagation | READY for newly processed records |
| Real-eval lessons available | See `evals/real/lesson_manifest.json`; new READY PDFs are candidates |

## Blockers

1. Install/configure an approved local ASR runtime and model for the two videos.
2. Human-verify source/document IDs and annotate concepts, relations, grounding, and quiz decisions.
3. Clean or exclude historical duplicate, corrupt, zero-chunk, and legacy records.
