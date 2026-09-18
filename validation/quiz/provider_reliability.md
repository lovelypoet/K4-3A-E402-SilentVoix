# Quiz Provider Reliability

This report separates external Gemini availability from the internal grounding,
validation, citation, and caching behavior. No human gold labels were used.

## Live smoke results

| Source | Difficulty | Result | Evidence | Attempts | Notes |
|---|---:|---|---:|---:|---|
| PDF `lesson_05` | EASY | PASS | 3 chunks / 470 chars | 1 | Validated and cached as `gemini_live` |
| PDF `lesson_05` | MEDIUM | FAIL | 3 chunks / 470 chars | 2–3 | Provider rate/availability errors or strict output rejection |
| Video `lesson_59` | EASY | PASS | 3 chunks / 292 chars | 1 | Validated and timestamp path remains supported |
| Video `lesson_59` | MEDIUM | FAIL | 3 chunks / 292 chars | 2 | Provider rate-limit response |

PDF live quiz: PASS for EASY; PARTIAL overall.

Video live quiz: PASS for EASY; PARTIAL overall.

PDF cached quiz: PASS in mocked cache tests.

Video cached quiz: PASS in mocked cache/timestamp tests.

## Provider observations

429 observed: 2 in the final sequential MEDIUM retry run.

503 observed: 3 in the final MEDIUM retry sequence; earlier smoke runs also observed
503 responses. The exact count is process-local through `/api/quiz/health` and is not
persisted as user analytics.

Grounding failures: 1 observed during the earlier PDF `gradient_descent` test; the
decision policy returned `DISAMBIGUATE` before any Gemini call.

Provider failures: MEDIUM requests that exhausted provider handling returned
`GENERATION_FAILED`; no quiz was fabricated.

## Resilience behavior

- Evidence is ranked and limited to 3 chunks by default, with a hard maximum of 5.
- Evidence text is limited to 6,000 characters and retains original chunk IDs.
- Gemini receives `E1`, `E2`, and `E3`, not document/page/timestamp metadata.
- Successful validated quizzes are stored in the ignored atomic JSON cache.
- Cache keys include lesson, concept, difficulty, source hash, prompt version, provider,
  and model.
- HTTP 503 receives bounded exponential retry with jitter.
- HTTP 429 receives bounded handling and is not aggressively retried.
- Deterministic fallback is opt-in and explicitly marked.
- Invalid, refused, or failed results are never cached.

## Internal correctness

The offline test suite passes 45 tests. It covers cache invalidation, cache hits,
provider bypass, source hash changes, prompt/model changes, PDF page citations, video
timestamps, short-output validation, 503 retry behavior, bounded 429 handling, and
fallback labeling.

