# AI Evaluation Framework

This package evaluates semantic quality separately from `pytest` software tests. It does not change prompts, models, extraction, grounding, or quiz behavior.

## Baseline

From the repository root on Windows:

```powershell
.venv\Scripts\python -m evals.run_eval
```

Optional filters:

```powershell
.venv\Scripts\python -m evals.run_eval --category quiz
.venv\Scripts\python -m evals.run_eval --category grounding
.venv\Scripts\python -m evals.run_eval --case-id QUIZ_001
```

The runner saves raw predictions, aggregate metrics, a quiz report, error analysis, and a fine-tuning decision under `evals/reports/`. The current 24-case set is synthetic and hand-curated. Synthetic results are regression evidence, not production validation. Human scores must be collected using `evals/human_review/` before making a fine-tuning decision.

The rubric is a proposed MVP rubric because the current project specification does not define a quiz scoring rubric: ten dimensions scored 0-2 for a maximum of 20. Critical failures force `fail` regardless of total score.
