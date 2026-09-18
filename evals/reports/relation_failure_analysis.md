# Relation Failure Analysis

## Summary

Four evaluation cases report relation precision failure: `CONCEPT_002`, `RELATION_001`, `GROUNDING_005`, and `QUIZ_001`. They all contain the same extra edge:

`gradient_descent -> loss_function : used_for`

The edge is emitted by the deterministic `RELATION_MAP`, not by an LLM. The source text in these cases either says gradient descent minimizes a loss function or explicitly states that a loss function is a prerequisite. Therefore the edge is semantically plausible in some cases, while the gold set expects only the prerequisite edge. This makes the current result partly a gold-contract problem rather than four independent semantic failures.

| Case | Expected relation | Actual extra relation | Direction | Evidence | Assessment | Primary cause |
|---|---|---|---|---|---|---|
| CONCEPT_002 | `loss_function->gradient_descent:prerequisite_of` | `gradient_descent->loss_function:used_for` | inverse/extra | `c002a` says minimizes | Co-occurrence plus explicit use language; gold is incomplete if `used_for` is allowed | `GROUND_TRUTH_ERROR` |
| RELATION_001 | `loss_function->gradient_descent:prerequisite_of` | `gradient_descent->loss_function:used_for` | inverse/extra | `r001` only explicitly supports prerequisite | Inferred inverse is not explicitly stated | `VALIDATOR` |
| GROUNDING_005 | prerequisite | extra `used_for` | inverse/extra | `g005a` says minimizes | Extra edge comes from same hard-coded map | `GROUND_TRUTH_ERROR` |
| QUIZ_001 | prerequisite | extra `used_for` | inverse/extra | `q001` says used to minimize | Gold omits a plausible edge | `GROUND_TRUTH_ERROR` |

## Root cause

The first wrong step is relation construction: `extract_relationships` iterates every node pair and emits every relation in a hard-coded map whenever both labels occur in the chunk. It does not require relation-specific lexical evidence, does not suppress inverse/duplicate semantic edges, and does not distinguish explicitly stated relationships from inferred ones. `validate_relationship` only checks membership in the allowed vocabulary.

This is deterministic behavior, not model capability. The relation evaluator also uses a strict set comparison, so an omitted but plausible gold edge becomes a false positive.

## Required diagnosis before fixing

1. The relation vocabulary must define whether `used_for` and `prerequisite_of` may coexist for the same pair.
2. Gold labels must include all accepted relations or explicitly mark unsupported/inferred relations.
3. Each relation should require evidence specific to its type and direction; mere co-occurrence is insufficient.
4. Evaluation should separate explicit-edge precision from optional inferred-edge precision.

## Recommended fix order

1. Correct and normalize the gold relation contract.
2. Add deterministic relation-evidence and direction checks.
3. Add a graph validator for duplicate, inverse, and unsupported edges.
4. Re-run the fixed evaluation set.
5. Only then assess whether any residual semantic relation errors remain.

No prompt change, model change, or fine-tuning is justified by these four cases.
