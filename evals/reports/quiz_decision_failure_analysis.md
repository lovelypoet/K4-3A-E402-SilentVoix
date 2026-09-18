# Quiz Decision Failure Analysis

## Decision-path traces

### RELATION_004

`gradient_descent` requested
-> graph contains requested node
-> node has one source record (`r004`)
-> `decide_quiz` returns `GENERATE_QUIZ`
-> `generate_quiz` uses the default question/options
-> structural citation exists
-> final unsafe generated quiz

**First wrong step:** decision policy. The source is a mention-only chunk and the lesson contains a competing concept, `gradient_boosting`. The policy does not inspect evidence strength or competing concepts.

### QUIZ_004

`gradient_descent` requested
-> graph contains requested node
-> node has one source record (`q004a`)
-> `decide_quiz` returns `GENERATE_QUIZ`
-> default question/options are generated
-> `q004a` citation passes identifier checks
-> final output is generated instead of disambiguating

**First wrong step:** decision policy at the retrieval boundary. The requested node's source is retrieved, but neighboring concept context (`q004b`) is not considered for ambiguity.

### QUIZ_005

`softmax` requested
-> graph contains requested node
-> node has one source record (`q005`)
-> `decide_quiz` returns `GENERATE_QUIZ`
-> default question/options about loss minimization are generated
-> `q005` citation exists structurally
-> final unsupported quiz

**First wrong step:** decision policy. A mention-only source is incorrectly scored as sufficient.

## Shared cause

`decide_quiz` currently returns `GENERATE_QUIZ` whenever the requested node exists and has any source records. The `len(sources)` branch returns `GENERATE_QUIZ` for both one and multiple sources, so `DISAMBIGUATE` is unreachable for normal graph input. `generate_quiz` then uses a default question bank and fixed options for unsupported concepts, while no claim-level validator rejects the mismatch.

## Diagnosis

| Case | Expected | Actual | Policy too permissive? | Retrieval issue? | Validator gap? | Prompt/model evidence? |
|---|---|---|---|---|---|---|
| RELATION_004 | DISAMBIGUATE | GENERATE_QUIZ | Yes | Weak context accepted | Yes | None |
| QUIZ_004 | DISAMBIGUATE | GENERATE_QUIZ | Yes | Competing concept omitted | Yes | None |
| QUIZ_005 | REFUSE_UNGROUNDED | GENERATE_QUIZ | Yes | Correct weak chunk retrieved | Yes | None |

All three are fixable without training. Recommended order: explicit evidence-strength policy, ambiguity-aware retrieval context, then deterministic question/answer/citation semantic validation.
