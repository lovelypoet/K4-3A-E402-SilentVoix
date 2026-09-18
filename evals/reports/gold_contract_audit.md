# Gold Contract Audit

The synthetic gold set was audited before Iteration 1. These are explicit corrections, not silent metric changes.

| Case | Previous expectation | Corrected expectation | Evidence and reason |
|---|---|---|---|
| `CONCEPT_005` | `expected_source = c005 slide 6` while expected decision was `REFUSE_UNGROUNDED` | `expected_source = null` | The text only mentions examples and a table. A refusal must not require a positive citation. |
| `GROUNDING_003` | Expected citation `wrong` / slide `999` | Expected citation `g003` / slide `21` | The only source is `g003` slide 21 and it directly supports regression. The old value was an invalid positive label; negative-source traps need a separate `forbidden_sources` field. |
| `RELATION_005` | Expected decision `GENERATE_QUIZ` | Expected decision `DISAMBIGUATE` | The source only says classification and clustering appear together; it provides no definition or claim support. The corrected decision follows the evidence policy for ambiguous/insufficient context. |

The relation gold labels were retained for this iteration. They specify explicit lesson relations, while the extractor's inferred `used_for` behavior was constrained separately. This keeps relation-contract behavior visible rather than silently rewriting relation truth.