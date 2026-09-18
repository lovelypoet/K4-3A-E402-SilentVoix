# Root Cause Summary

## Baseline

- Total evaluation cases: 26
- Unique failing cases: 10
- Synthetic cases: 26
- Real cases: 0
- Software tests: 18 passed, 51 existing deprecation warnings
- No prompt, model, or pipeline behavior was changed during diagnosis.

## Root cause distribution

Primary labels are assigned once per unique failing case.

| Primary root cause | Cases | Case IDs |
|---|---:|---|
| DATA | 0 | |
| SOURCE_METADATA | 0 | |
| SOURCE_MAPPING | 0 | |
| RETRIEVAL | 0 | |
| DECISION_POLICY | 3 | `RELATION_004`, `QUIZ_004`, `QUIZ_005` |
| PROMPT | 0 | |
| VALIDATOR | 2 | `RELATION_001`, `QUIZ_006` |
| MODEL_CAPABILITY | 0 | |
| GROUND_TRUTH_ERROR | 5 | `CONCEPT_002`, `CONCEPT_005`, `GROUNDING_003`, `GROUNDING_005`, `QUIZ_001` |

`QUIZ_004` has retrieval as a secondary cause because the decision context omits competing concepts. `QUIZ_005` has validator as a secondary cause because structural citation validation does not assess claim support. The four relation precision cases share one underlying hard-coded relation-map issue; their primary labels differ only where the gold contract is clearly incomplete versus where direction evidence is clearly absent.

## Answers to the required questions

### 1. What percentage is clearly fixable without training?

10/10 unique failing cases, or **100%**, are explainable by decision policy, deterministic validation, or evaluation/gold-contract defects. The correct fixes are evidence thresholds, ambiguity-aware context, claim-level citation checks, phrase-boundary extraction, relation-specific evidence rules, and normalized gold labels.

### 2. What percentage is unresolved?

**0/10** are unresolved after inspecting the input text, graph, citations, decision path, and source metadata. Some need a product-contract decision, especially whether `used_for` should coexist with `prerequisite_of`.

### 3. How many show model capability limits?

**0/10.** The current implementation uses deterministic pattern matching, hard-coded relations, fixed quiz templates, and deterministic decision logic. No failure survives the simpler explanations required before assigning `MODEL_CAPABILITY`.

### 4. Which component is the true bottleneck?

The primary product bottleneck is **evidence sufficiency and quiz decision policy**, supported by a missing claim-level validator. The current rule is effectively `node exists + any source metadata => GENERATE_QUIZ`; it cannot distinguish a definition from a mention, cannot detect competing concepts, and cannot verify that the generated question/answer is entailed by the cited text.

The secondary bottleneck is the relation contract: the extractor emits hard-coded edges based on co-occurrence and the gold set does not consistently define whether inferred `used_for` edges are accepted.

### 5. Is fine-tuning justified?

**No. Use: MORE REAL DATA REQUIRED BEFORE DECISION.** The dataset is entirely synthetic, has no human quiz labels, and no failure demonstrates model capability limitation. Fine-tuning would be premature before fixing gold contracts, evidence policy, deterministic validators, and source/context selection on real lessons.

## Severity distribution

| Severity | Count | Cases |
|---|---:|---|
| CRITICAL | 3 | `RELATION_004`, `QUIZ_004`, `QUIZ_005` |
| HIGH | 3 | `CONCEPT_002`, `RELATION_001`, `QUIZ_001` |
| MEDIUM | 2 | `GROUNDING_005`, `QUIZ_006` |
| LOW | 2 | `CONCEPT_005`, `GROUNDING_003` fixture-only citation mismatches |

Severity is assigned to observed product risk, not merely the metric mismatch. `GROUNDING_003` is not a product citation failure because the actual citation is correct; it is a malformed negative test and is discussed as a gold-contract defect.

## Recommended next actions, in order

1. Repair the evaluation schema: separate positive expected citations from invalid/forbidden citation cases and define accepted relation closure.
2. Add deterministic evidence sufficiency rules: mention-only text must not generate a quiz.
3. Make `DISAMBIGUATE` reachable by checking competing concepts and ambiguous requests.
4. Add claim-level quiz validation for concept alignment, answer support, explanation support, and citation support.
5. Add phrase-boundary/longest-match handling so `feature_vector` does not also create `vector`.
6. Add relation-specific lexical evidence and direction checks.
7. Re-run on 5-10 clean real lessons with human labels before considering prompt changes or fine-tuning.

## Real-data follow-up plan

Keep synthetic regression cases separate from human-labeled quality results. Select 5-10 clean real lessons, deduplicate by source, assign globally unique document/chunk/source IDs, manually label concepts and relations, review each citation, and collect 30-60 quiz examples across easy/medium/hard difficulty. Include unsupported and ambiguous requests. Obtain lecturer review where possible using `evals/human_review/quiz_review_template.csv` and `.json`. Report synthetic and real metrics in separate sections; do not combine them into a production claim.
