# Lesson Studio AI Evaluation Summary

## Software

- Tests: **24 passed**
- Warnings: **51 existing deprecation warnings**

## Synthetic evaluation

- Cases: **26**, all synthetic; real human-labeled cases: **0**
- Ground-truth corrections: **3** (`CONCEPT_005`, `GROUNDING_003`, `RELATION_005`)
- Concept F1: **1.000**
- Relation F1: **1.000**
- Citation accuracy: **0.692**
- Source recall: **1.000**
- Unsupported claim rate: **0.308**
- Decision accuracy: **1.000**
- False `GENERATE_QUIZ`: **0**
- False refusal: **0**
- Critical quiz failures: **5**

## Quiz semantic quality

- Publishable quizzes: **10**
- Semantic mean: **20/20** for the 10 quizzes that passed validation
- Strong: **10**
- Acceptable: **0**
- Needs improvement: **0**
- Fail: **0** among publishable outputs
- Five additional generated candidates were withheld by deterministic validation; this is a safety result, not a passing quiz score.
- Wrong-answer cases: **0** detected in publishable outputs
- Multiple-correct cases: **0** detected in publishable outputs
- Grounding failures: **5 withheld outputs**
- Difficulty mismatches: not yet independently human-labeled
- Distractor failures: not yet independently human-labeled
- Explanation hallucinations: not yet independently human-labeled
- Concept misalignments: caught by validator in withheld outputs

## Real evaluation

- Lessons: **0 human-validated**
- Cases: **0**
- Quiz cases: **0**
- Human reviewers: **0**
- Metrics: unavailable; see `evals/real/lesson_manifest.json` and `evals/real/README.md`.

## Quality bar

- At least 80% expected behavior: **PASS on decision behavior; overall production result INCONCLUSIVE**
- Citation accuracy at least 90%: **FAIL** (`0.692`)
- Zero unsupported-grounded critical failures: **PASS for returned quizzes; five candidates were withheld**
- Synthetic result: **INCONCLUSIVE**
- Real result: **INCONCLUSIVE**

## Diagnosis

- Primary bottleneck: claim-level quiz grounding and semantic validation.
- Root cause: previous false generations came from permissive evidence policy; Iteration 1 now blocks them. Remaining evidence gaps require real human-labeled data.
- Failures fixable without training: **10/10 diagnosed cases**
- Model capability failures: **0/10**
- Fine-tuning decision: **MORE REAL DATA REQUIRED BEFORE DECISION**

## Next recommended action

Repair/re-ingest the real corpus, assign globally safe source IDs, annotate 5-10 clean source-group-separated lessons, and collect 30-60 lecturer/student-reviewed quiz cases before comparing further prompt, retrieval, policy, or validator changes.
