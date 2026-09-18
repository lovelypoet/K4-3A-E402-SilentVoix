# Validation

This folder contains evidence used to validate the Lesson Studio MVP.

## Ingestion validation

The five newly supplied PDFs were processed with digital PDF extraction. Both newly supplied local videos were transcribed with `faster-whisper` small on CPU. Source identity uses `file:<sha256>` and new chunks carry document, lesson, source-group, and page/timestamp metadata.

## AI/KG validation

Synthetic evaluation exists. Iteration 1 reached Concept F1 1.000, Relation F1 1.000, Source Recall 1.000, and Decision Accuracy 1.000. These are regression results, not production validation.

## Quiz validation

No human quiz reviews have been fabricated. The review template is ready under `quiz/`.

### Runtime quiz generation

The previous `QUESTION_BANK` implementation remains available for deterministic unit
tests and fallback experiments, but is no longer the production frontend path. The
production endpoint is `POST /api/quiz/generate`. It retrieves lesson chunks, applies
the existing decision policy before any model call, sends only selected evidence to
the server-side Gemini provider, resolves citations from chunk metadata, and runs the
deterministic post-generation validator. PDF page and video timestamp metadata are
preserved. Missing API keys, provider failures, malformed drafts, unsupported, and
ambiguous evidence return explicit safe failure decisions rather than fabricated quiz
content.

## User validation

Seven clean real-evaluation candidates are now available: five PDF lessons and two timestamped video lessons. Human labels are being prepared; no real human labels are currently claimed.

## Real Evaluation Status

- 7 real source candidates available
- 5 primary lessons selected for human annotation
- Human annotation packs prepared
- Human labels pending
- Quiz human review pending
- No fine-tuning performed

See `evals/real/evaluation_split.md` for the frozen development/hold-out protocol. The five primary lessons must not also serve as the final uncontaminated evaluation after prompt or validator changes.

## Fine-tuning decision

No fine-tuning has been justified. Model capability failures have not been demonstrated. The current bottleneck remains grounding/citation safety and real human validation.
