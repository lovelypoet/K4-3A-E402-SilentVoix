# Validation

This folder contains evidence used to validate the Lesson Studio MVP.

## Ingestion validation

The five newly supplied PDFs were processed with digital PDF extraction. Both newly supplied local videos were registered, but transcription is currently blocked because the optional `faster-whisper` runtime is not installed. Source identity uses `file:<sha256>` and new chunks carry document, lesson, source-group, and page/timestamp metadata.

## AI/KG validation

Synthetic evaluation exists. Iteration 1 reached Concept F1 1.000, Relation F1 1.000, Source Recall 1.000, and Decision Accuracy 1.000. These are regression results, not production validation.

## Quiz validation

No human quiz reviews have been fabricated. The review template is ready under `quiz/`.

## User validation

Human-labeled real evaluation is being prepared. No real human labels are currently claimed.

## Fine-tuning decision

No fine-tuning has been justified. Model capability failures have not been demonstrated. The current bottleneck remains grounding/citation safety and real human validation.
