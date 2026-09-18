# Failure Case Inventory

## Scope and reproducibility

- Evaluation cases: 26
- Unique failing cases: 10
- Dataset: 26 synthetic, hand-curated cases; 0 real cases
- Software tests: 18 passed, 51 existing deprecation warnings
- Evaluation rerun: reproducible at Concept F1 1.000, Relationship F1 0.909, citation accuracy 0.885, unsupported claim rate 0.115, decision accuracy 0.885
- No prompt, model, or pipeline behavior was changed during this diagnosis.

The baseline evaluator treats every `expected_source` as a positive citation target. Two fixtures use that field as an intentionally wrong or irrelevant source, so those are analyzed as gold/evaluator design problems rather than model failures.

## Case-by-case inventory

### CONCEPT_002

- **Category:** concept / relation
- **Expected:** concepts `gradient_descent`, `loss_function`; relation `loss_function->gradient_descent:prerequisite_of`; generate quiz; citation `c002b` slide 3.
- **Actual:** concepts correct; relations include the expected prerequisite plus extra `gradient_descent->loss_function:used_for`; quiz generated with citations `c002a` and `c002b`.
- **Input source:** `c002a`: "Gradient descent minimizes a loss function." `c002b`: "The loss function measures prediction error."
- **Expected evidence:** `c002b` supports the loss-function answer; `c002a` supports the optimization statement.
- **Retrieved evidence:** both node source records, because retrieval returns every source attached to the concept.
- **Generated output:** extra `used_for` edge and two citations.
- **Source sufficient?** Yes.
- **Ground-truth label correct?** Partially. The gold relation list omits a plausible `used_for` relation supported by `c002a`.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Yes, but broader than the expected single citation.
- **Citation target correct?** `c002b` is correct; `c002a` is topically relevant but not necessary for the expected answer.
- **Decision possible?** Yes.
- **Deterministic validation gap?** The validator does not compare edge evidence and relation semantics against a gold relation contract.
- **Prompt issue?** None; this path is deterministic.
- **Model limitation evidence?** None.
- **Primary root cause:** `GROUND_TRUTH_ERROR`
- **Secondary cause:** `VALIDATOR`
- **Severity:** HIGH (only if the omitted relation is truly disallowed; otherwise LOW gold mismatch)

### CONCEPT_005

- **Category:** concept / grounding
- **Expected:** no concepts, refusal; `expected_source` is `c005` slide 6.
- **Actual:** no concepts and refusal with no citations.
- **Input source:** `c005`: "This lecture contains examples and a table of results."
- **Expected evidence:** no evidence for a requested learning concept.
- **Retrieved evidence:** none.
- **Generated output:** refusal and empty citation list.
- **Source sufficient?** No.
- **Ground-truth label correct?** The refusal label is correct; the positive `expected_source` is inconsistent with it.
- **Source metadata correct?** Metadata is structurally valid, but it does not support the requested concept.
- **Retrieved chunk correct?** Yes: nothing relevant should be retrieved.
- **Citation target correct?** No positive citation should exist.
- **Decision possible?** Yes, refusal is the correct decision.
- **Deterministic validation gap?** The evaluator cannot distinguish a negative refusal case from a positive citation case when `expected_source` is populated.
- **Prompt issue?** None.
- **Model limitation evidence?** None.
- **Primary root cause:** `GROUND_TRUTH_ERROR`
- **Secondary cause:** `VALIDATOR`
- **Severity:** LOW (evaluation fixture defect, not product behavior)

### RELATION_001

- **Category:** relation
- **Expected:** only `loss_function->gradient_descent:prerequisite_of`.
- **Actual:** expected prerequisite plus `gradient_descent->loss_function:used_for`.
- **Input source:** `r001`: "A loss function is a prerequisite for understanding gradient descent."
- **Expected evidence:** explicit prerequisite direction from loss function to gradient descent.
- **Retrieved evidence:** `r001` for both generated edges.
- **Generated output:** inverse `used_for` edge is generated from the hard-coded relation map even though the sentence explicitly expresses prerequisite direction.
- **Source sufficient?** Yes for the prerequisite; not explicit enough to justify an inverse `used_for` edge under a strict relation contract.
- **Ground-truth label correct?** Likely incomplete if `used_for` is intended as a semantic inverse; otherwise correct under a one-edge gold contract.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Yes.
- **Citation target correct?** Yes.
- **Decision possible?** Yes.
- **Deterministic validation gap?** There is no direction/evidence rule that suppresses inverse edges not explicitly stated.
- **Prompt issue?** None; deterministic relation extraction.
- **Model limitation evidence?** None.
- **Primary root cause:** `VALIDATOR`
- **Secondary cause:** `GROUND_TRUTH_ERROR`
- **Severity:** HIGH

### RELATION_004

- **Category:** relation / decision
- **Expected:** no relation; `DISAMBIGUATE`.
- **Actual:** no relation; `GENERATE_QUIZ` for `gradient_descent`.
- **Input source:** `r004`: "The lecture mentions gradient descent and gradient boosting."
- **Expected evidence:** co-occurrence only; no relation evidence and no explanatory definition.
- **Retrieved evidence:** the requested node has one source record, `r004`.
- **Generated output:** default quiz with generic options and citation `r004`.
- **Source sufficient?** Insufficient for a grounded quiz; the requested term is named but not explained.
- **Ground-truth label correct?** Reasonable, but the fixture needs a formal definition of why explicit mention is insufficient.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Yes, but weak context was accepted as sufficient.
- **Citation target correct?** It exists and identifies the chunk, but the text does not support the generated answer.
- **Decision possible?** Yes; disambiguation or refusal is possible from the weak evidence.
- **Deterministic validation gap?** Evidence sufficiency checks only node/source existence.
- **Prompt issue?** Not reached; the decision layer fails first.
- **Model limitation evidence?** None.
- **Primary root cause:** `DECISION_POLICY`
- **Secondary cause:** `DATA`
- **Severity:** CRITICAL (unsafe false generate)

### GROUNDING_003

- **Category:** grounding
- **Expected:** citation `{document_id: doc_grounding, chunk_id: wrong, slide: 999}`.
- **Actual:** citation `g003`, slide 21, which is the only real source in the input.
- **Input source:** `g003`: "Regression predicts continuous values."
- **Expected evidence:** the actual source is `g003` slide 21; the expected citation is intentionally invalid.
- **Retrieved evidence:** `g003`.
- **Generated output:** citation to the actual source.
- **Source sufficient?** Yes.
- **Ground-truth label correct?** No, not as a positive gold citation. This is a negative/adversarial fixture represented with the wrong schema.
- **Source metadata correct?** Actual metadata is correct; expected metadata is not.
- **Retrieved chunk correct?** Yes.
- **Citation target correct?** Actual citation is correct.
- **Decision possible?** Yes.
- **Deterministic validation gap?** The evaluator needs an explicit `invalid_expected_source` or negative-citation field.
- **Prompt issue?** None.
- **Model limitation evidence?** None.
- **Primary root cause:** `GROUND_TRUTH_ERROR`
- **Secondary cause:** `VALIDATOR`
- **Severity:** LOW (evaluation design defect; not a fabricated citation)

### GROUNDING_005

- **Category:** grounding / relation
- **Expected:** prerequisite relation and citation `g005a` slide 23.
- **Actual:** prerequisite plus extra `used_for`; citations `g005a` and `g005b`.
- **Input source:** `g005a`: "Gradient descent minimizes a loss function." `g005b`: "Gradient descent updates parameters using the gradient."
- **Expected evidence:** `g005a` directly supports the loss-function relationship; `g005b` is additional evidence about gradient descent.
- **Retrieved evidence:** both sources attached to the concepts.
- **Generated output:** both valid source records, plus the extra relation.
- **Source sufficient?** Yes.
- **Ground-truth label correct?** Citation gold is too narrow for a multi-source case; the extra relation is the same relation-map issue as the other three cases.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Yes.
- **Citation target correct?** Both citation targets exist; `g005a` is the direct target for the expected claim.
- **Decision possible?** Yes.
- **Deterministic validation gap?** No claim-level citation selection or relation-direction check.
- **Prompt issue?** None.
- **Model limitation evidence?** None.
- **Primary root cause:** `GROUND_TRUTH_ERROR`
- **Secondary cause:** `VALIDATOR`
- **Severity:** MEDIUM

### QUIZ_001

- **Category:** quiz / relation
- **Expected:** generate; expected prerequisite relation and citation `q001` slide 40.
- **Actual:** quiz is generated and cited correctly; extra `used_for` relation appears in the graph.
- **Input source:** `q001`: "Gradient descent is an optimization algorithm used to minimize a loss function."
- **Expected evidence:** the source supports the quiz answer and the graph's prerequisite relation, but also plausibly supports a use relation.
- **Retrieved evidence:** `q001`.
- **Generated output:** correct citation and answer contract; extra graph edge.
- **Source sufficient?** Yes.
- **Ground-truth label correct?** Relation list is incomplete if `used_for` is allowed as a direct relation.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Yes.
- **Citation target correct?** Yes.
- **Decision possible?** Yes.
- **Deterministic validation gap?** Relation contract does not distinguish explicit from inferred relations.
- **Prompt issue?** None.
- **Model limitation evidence?** None.
- **Primary root cause:** `GROUND_TRUTH_ERROR`
- **Secondary cause:** `VALIDATOR`
- **Severity:** HIGH for graph precision, not a quiz grounding failure

### QUIZ_004

- **Category:** quiz / decision
- **Expected:** `DISAMBIGUATE`.
- **Actual:** `GENERATE_QUIZ` for `gradient_descent`, citing `q004a`.
- **Input source:** `q004a`: "Gradient descent is an optimization algorithm." `q004b`: "Gradient boosting is an ensemble method."
- **Expected evidence:** two similarly named concepts are present; the requested concept has only a shallow definition.
- **Retrieved evidence:** only the requested node's `q004a` source is retrieved; the competing concept is not considered by the decision layer.
- **Generated output:** generic quiz with `q004a` citation.
- **Source sufficient?** Insufficient for the expected ambiguity policy.
- **Ground-truth label correct?** Reasonable, but the ambiguity rule is not encoded in the system contract.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Correct for the requested concept, incomplete for ambiguity detection.
- **Citation target correct?** It identifies the requested concept's chunk, but cannot resolve the competing concept context.
- **Decision possible?** Yes; decision should inspect neighboring/competing concepts.
- **Deterministic validation gap?** Decision sees only source count for the requested node and cannot detect competing concepts.
- **Prompt issue?** Not reached.
- **Model limitation evidence?** None.
- **Primary root cause:** `DECISION_POLICY`
- **Secondary cause:** `RETRIEVAL`
- **Severity:** CRITICAL

### QUIZ_005

- **Category:** quiz / decision
- **Expected:** `REFUSE_UNGROUNDED` because the source only mentions softmax.
- **Actual:** `GENERATE_QUIZ` with the default question, generic loss-function options, and citation `q005`.
- **Input source:** `q005`: "The lecture mentions softmax."
- **Expected evidence:** a name mention is not enough to support a question, answer, or explanation about softmax.
- **Retrieved evidence:** `q005` is returned because the softmax node has one source record.
- **Generated output:** default question unrelated to softmax semantics, answer "To minimize the value of a loss function.", citation `q005`.
- **Source sufficient?** No.
- **Ground-truth label correct?** Yes, under the stated insufficient-source policy.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Yes, but weak evidence was treated as sufficient.
- **Citation target correct?** The chunk exists but does not support the generated question or answer.
- **Decision possible?** Yes; refusal is deterministic from the absence of a meaningful definition.
- **Deterministic validation gap?** There is no concept-to-question semantic alignment or source-support check; the generic default bypasses this.
- **Prompt issue?** Not reached.
- **Model limitation evidence?** None; output is deterministic template behavior.
- **Primary root cause:** `DECISION_POLICY`
- **Secondary cause:** `VALIDATOR`
- **Severity:** CRITICAL

### QUIZ_006

- **Category:** quiz / concept
- **Expected:** only `feature_vector` for the source; refusal for unsupported `attention` request.
- **Actual:** concepts include `feature_vector` and extra `vector`; refusal for `attention` is correct.
- **Input source:** `q006`: "The lesson explains feature vectors."
- **Expected evidence:** `feature vectors` is one compound concept.
- **Retrieved evidence:** not relevant to the requested unsupported concept.
- **Generated output:** extra `vector` node caused by substring matching of `vector` inside `feature vector`.
- **Source sufficient?** Sufficient for `feature_vector`, not for `vector` as an independent concept.
- **Ground-truth label correct?** Yes.
- **Source metadata correct?** Yes.
- **Retrieved chunk correct?** Yes, but candidate extraction is too broad.
- **Citation target correct?** No quiz citation was generated for the unsupported request.
- **Decision possible?** Yes; refusal was correct.
- **Deterministic validation gap?** Concept matcher lacks phrase-boundary and longest-match suppression.
- **Prompt issue?** None; deterministic extraction.
- **Model limitation evidence?** None.
- **Primary root cause:** `VALIDATOR`
- **Secondary cause:** `DATA`
- **Severity:** MEDIUM

## Initial diagnosis

The four relation precision failures are the same deterministic relation-map behavior, but the gold set does not clearly state whether `used_for` is disallowed or merely omitted. The three false generations are genuine decision-policy failures: source existence is treated as evidence sufficiency, and competing concepts are not considered. The concept over-extraction is a deterministic phrase-matching issue. No case meets the strict definition of `MODEL_CAPABILITY` because every failure is explained by policy, deterministic logic, retrieval scope, or gold-fixture design.
