# False GENERATE Analysis

All three cases are unsafe because the pipeline generates grounded-looking quiz output without enough semantic evidence. None indicates model capability limitation; the decision layer is deterministic and permissive.

## RELATION_004

- **Expected:** `DISAMBIGUATE`
- **Actual:** `GENERATE_QUIZ`
- **Requested concept:** `gradient_descent`
- **Source:** `r004`, slide 13: "The lecture mentions gradient descent and gradient boosting."
- **Requested concept explicitly present?** Yes, by name.
- **Evidence for question/answer/explanation?** No meaningful definition or property; only mention.
- **Ambiguity:** Yes, two similarly named concepts co-occur.
- **Retrieved evidence:** one source record for the requested node.
- **Outside knowledge used?** The generated default answer is not supported by the source.
- **First wrong step:** `decide_quiz` sees a node with sources and returns `GENERATE_QUIZ`.
- **Decision path:** requested concept -> node exists -> one source record -> generate -> default quiz -> citation existence only -> final unsafe output.
- **Primary root cause:** `DECISION_POLICY`
- **Secondary cause:** `DATA`
- **Severity:** CRITICAL
- **Recommended fix:** require semantic evidence, detect competing concepts, and route shallow mentions to `DISAMBIGUATE` or `REFUSE_UNGROUNDED`.

## QUIZ_004

- **Expected:** `DISAMBIGUATE`
- **Actual:** `GENERATE_QUIZ`
- **Requested concept:** `gradient_descent`
- **Sources:** `q004a`: "Gradient descent is an optimization algorithm." `q004b`: "Gradient boosting is an ensemble method."
- **Requested concept explicitly present?** Yes.
- **Evidence for question/answer/explanation?** Some evidence for gradient descent, but the case's expected policy treats the near-name competitor as ambiguity.
- **Ambiguity:** Yes at lesson context level; the decision layer only examines the requested node.
- **Retrieved evidence:** `q004a` is retrieved; `q004b` is omitted from the decision context.
- **Outside knowledge used?** The default quiz template supplies generic content rather than resolving ambiguity.
- **First wrong step:** retrieval/decision boundary: `decide_quiz` does not inspect competing concepts or lesson context.
- **Decision path:** requested concept -> requested node exists -> one source record -> generate -> default quiz -> citation check passes structurally -> final output.
- **Primary root cause:** `DECISION_POLICY`
- **Secondary cause:** `RETRIEVAL`
- **Severity:** CRITICAL
- **Recommended fix:** use a lesson-level candidate context and an explicit ambiguity rule before generation.

## QUIZ_005

- **Expected:** `REFUSE_UNGROUNDED`
- **Actual:** `GENERATE_QUIZ`
- **Requested concept:** `softmax`
- **Source:** `q005`, slide 45: "The lecture mentions softmax."
- **Requested concept explicitly present?** Yes, by name only.
- **Evidence for question/answer/explanation?** No. The generated default question and loss-function options are unrelated to softmax.
- **Ambiguity:** Not required; evidence is simply insufficient.
- **Retrieved evidence:** `q005` is returned because the node has a source record.
- **Outside knowledge used?** The default options are unrelated content, so the output is unsupported.
- **First wrong step:** source existence is treated as evidence sufficiency in `decide_quiz`.
- **Decision path:** requested concept -> node exists -> one source record -> generate -> default quiz unrelated to concept -> structural citation check passes -> final output.
- **Primary root cause:** `DECISION_POLICY`
- **Secondary cause:** `VALIDATOR`
- **Severity:** CRITICAL
- **Recommended fix:** require a concept definition/property evidence threshold and validate question/answer semantic alignment to the requested concept before generation.

## Common conclusion

The policy currently implements `node exists and sources non-empty => GENERATE_QUIZ`. It never returns `DISAMBIGUATE` for multiple or competing concepts, despite the public decision vocabulary supporting that state. A deterministic evidence validator could catch all three cases without prompt changes or training.
