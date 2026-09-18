# Real Human-Labeled Evaluation

This directory intentionally contains no fabricated gold labels. `lesson_manifest.json` records the available lesson inventory and exclusion reasons. `gold_cases.json` remains empty until a reviewer labels source-grounded concepts, relations, citations, and quiz decisions.

The current corpus contains five newly extracted PDF candidates with unique SHA-256 source groups and complete new chunk metadata. The two newly supplied local videos are registered but remain excluded until transcription succeeds. Historical duplicate transcript source groups, encoding corruption, missing document IDs, zero-chunk documents, and low-information extraction remain excluded.

After annotation, store cases in `gold_cases.json` and run a separate real evaluator that writes `evals/reports/real_baseline.json`, `real_baseline.md`, and `real_error_analysis.md`. Never combine these results with synthetic metrics.
