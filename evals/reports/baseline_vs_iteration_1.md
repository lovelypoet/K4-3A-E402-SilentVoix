# Baseline vs Iteration 1

Ground-truth corrections mean some deltas are not attributable to pipeline behavior alone. Iteration 1 also adds evidence policy and deterministic validation; synthetic results remain non-production evidence.

| Metric | Original Baseline | Iteration 1 | Delta |
|---|---:|---:|---:|
| Concept F1 | 1.000 | 1.000 | +0.000 |
| Relation F1 | 0.909 | 1.000 | +0.091 |
| Citation Accuracy | 0.885 | 0.692 | -0.193 |
| Source Recall | 0.923 | 1.000 | +0.077 |
| Unsupported Claim Rate | 0.115 | 0.308 | +0.193 |
| Decision Accuracy | 0.885 | 1.000 | +0.115 |
| False GENERATE | 3 | 0 | -3 |
| False REFUSE | 0 | 0 | +0 |
| Critical Quiz Failures | 3 | 5 | +2 |

The quality bar remains frozen: at least 80% expected behavior, citation accuracy at least 90%, and zero unsupported-grounded critical failures.
