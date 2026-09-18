# Citation Failure Analysis

The baseline reports three citation failures. Inspection shows that one is a real unsupported citation and two are evaluation-fixture contract problems.

| Case | Cited chunk exists? | Lesson/document correct? | Metadata correct? | Text supports claim? | Diagnosis | Primary cause |
|---|---|---|---|---|---|---|
| CONCEPT_005 | No citation generated | N/A | Input metadata exists | No source supports the requested `examples` concept | Refusal is correct, but `expected_source` incorrectly demands a positive citation | `GROUND_TRUTH_ERROR` |
| GROUNDING_003 | Yes: `g003` | Yes | Yes: slide 21 | Yes: regression predicts continuous values | Actual citation is correct; gold expects intentionally invalid `wrong`/slide 999 without a negative expected-source field | `GROUND_TRUTH_ERROR` |
| QUIZ_005 | Yes: `q005` | Yes | Yes: slide 45 | No: "The lecture mentions softmax" cannot support the generated default question or loss-function answer | Real unsupported citation and false generation | `DECISION_POLICY` |

## CONCEPT_005

The requested concept is `examples`, but extraction finds no concept and the system correctly refuses with no citation. The fixture simultaneously marks `c005` as `expected_source`, which conflicts with the refusal expectation. This is a gold/evaluator schema problem, not missing retrieval. The case should use `expected_source: null` and optionally an explicit `source_exists_but_unsupported` label.

## GROUNDING_003

The source contains only `g003` on slide 21. The system cites that real source. The expected citation `{chunk_id: wrong, slide: 999}` is not a valid positive ground truth and appears intended to test incorrect-source behavior. The dataset needs fields such as `citation_expectation: INVALID` or `forbidden_sources`, rather than treating a fabricated source as the correct citation.

## QUIZ_005

The citation record exists and has correct document/chunk/slide metadata, but the text is only a mention. It does not support the question, correct answer, or explanation. This is the real citation failure. The first wrong step is decision policy, which treats source presence as source sufficiency. A citation-existence validator passes the output because it checks IDs, not claim-level semantic support.

## Required distinction

A citation must be evaluated at three levels:

1. Identifier validity: document/chunk/slide/timestamp exists.
2. Source mapping: the citation belongs to the requested concept and lesson.
3. Claim support: the cited text actually entails the question, answer, and explanation.

The current system only reliably supports level 1 and partial level 2. No citation failure is evidence of model capability because the failing behavior is deterministic or caused by invalid gold semantics.
