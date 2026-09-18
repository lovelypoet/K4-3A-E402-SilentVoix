# AI Evaluation Baseline

This is an AS-IS baseline. The dataset is synthetic and must not be presented as real-world validation.

- Dataset: 26 cases (26 synthetic, 0 real)
- Concept F1: 1.000
- Relationship F1: 1.000
- Citation accuracy: 0.692
- Unsupported claim rate: 0.308
- Quiz decision accuracy: 1.000
- False GENERATE: 0
- False REFUSE: 0
- Quiz mean score: 20.00/20
- Quiz acceptable-or-better rate: 1.000
- Critical quiz failures: 5

## Quality bar

The proposed MVP bar is at least 80% expected behavior, citation accuracy at least 90%, and zero critical unsupported-grounded generation. Synthetic-only results are **INCONCLUSIVE** for production quality.

## Decision

Fine-tuning decision: MORE REAL DATA REQUIRED BEFORE DECISION.

Use `evals.reports/raw_predictions.json` for per-case predictions and `python -m evals.run_eval --category quiz` for a filtered run.
