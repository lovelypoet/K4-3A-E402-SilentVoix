# Error Analysis

All 26 cases are synthetic hand-curated fixtures; these results are not production validation.

## Failure categories

- **GROUNDING: wrong or missing citation**: 8
- **QUIZ: post-generation semantic validation withheld the quiz**: 5
- **RELATION: missing edge or wrong direction/type**: 2

## Interpretation

Failures should be triaged in this order: data/source metadata, deterministic validators, grounding/retrieval, prompt constraints, then model capability. This baseline does not justify fine-tuning by itself.
