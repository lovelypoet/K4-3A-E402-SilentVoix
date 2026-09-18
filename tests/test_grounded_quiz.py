from ai.quiz.grounded import generate_grounded_quiz
from ai.quiz.schema import QuizDraft
from ai.quiz.providers.base import QuizProvider
from ai.quiz.providers.gemini import GeminiProvider
from ai.quiz.cache import QuizCache
from ai.quiz.retrieval import evidence_character_count, select_evidence
from ai.quiz.validator import validate_draft_constraints
import httpx


class FakeProvider(QuizProvider):
    provider_name = "fake"
    model = "fake-model"

    def __init__(self, draft=None, error=None):
        self.calls = 0
        self.draft = draft
        self.error = error

    def generate_quiz_from_evidence(self, concept, evidence, difficulty):
        self.calls += 1
        if self.error:
            raise self.error
        return self.draft


def graph(decision_text="Gradient descent minimizes a loss function during model training."):
    return {
        "lesson_id": "lesson_pdf",
        "nodes": [{
            "id": "gradient_descent", "label": "Gradient Descent", "description": "optimization",
            "sources": [{"document_id": "doc_pdf", "chunk_id": "chunk_1", "page": 7, "text": decision_text}],
        }],
        "edges": [],
    }


def valid_draft():
    return QuizDraft(
        question="What does gradient descent minimize?",
        options=["A loss function", "A page number", "A video timestamp", "A file name"],
        correct_index=0, explanation="The evidence states that gradient descent minimizes a loss function.",
        used_evidence_ids=["E1"],
    )


def test_supported_evidence_calls_provider_and_resolves_pdf_citation(tmp_path):
    provider = FakeProvider(valid_draft())
    result = generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", provider, cache=QuizCache(tmp_path / "cache.json"))
    assert provider.calls == 1
    assert result.decision == "GENERATE_QUIZ"
    assert result.validation.passed is True
    assert result.correct_option == "A"
    assert result.citations[0].document_id == "doc_pdf"
    assert result.citations[0].page == 7


def test_unsupported_evidence_does_not_call_provider(tmp_path):
    provider = FakeProvider(valid_draft())
    result = generate_grounded_quiz(graph("This source mentions gradient descent."), "lesson_pdf", "gradient_descent", "medium", provider, cache=QuizCache(tmp_path / "cache.json"))
    assert provider.calls == 0
    assert result.decision == "REFUSE_UNGROUNDED"


def test_provider_failure_is_explicit(tmp_path):
    provider = FakeProvider(error=RuntimeError("offline"))
    result = generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "medium", provider, cache=QuizCache(tmp_path / "cache.json"))
    assert result.decision == "GENERATION_FAILED"
    assert result.validation.passed is False


def test_video_timestamp_is_preserved(tmp_path):
    source_graph = graph()
    source_graph["nodes"][0]["sources"][0] = {
        "document_id": "doc_video", "chunk_id": "chunk_v", "start_time": 132.4,
        "end_time": 158.7, "text": "Gradient descent minimizes a loss function during model training.",
    }
    draft = valid_draft().model_copy(update={"used_evidence_ids": ["E1"]})
    result = generate_grounded_quiz(source_graph, "lesson_video", "gradient_descent", "medium", FakeProvider(draft), cache=QuizCache(tmp_path / "cache.json"))
    assert result.validation.passed is True
    assert result.citations[0].start_time == 132.4
    assert result.citations[0].end_time == 158.7


def test_retrieval_defaults_to_three_and_removes_duplicates_and_respects_budget():
    evidence = [{"chunk_id": f"c{i}", "text": "Gradient descent minimizes the loss function. " + ("detail " * i)} for i in range(6)]
    selected = select_evidence({"id": "gradient_descent", "label": "Gradient Descent"}, evidence, max_chars=180)
    assert len(selected) <= 3
    assert len(selected) <= 5
    assert evidence_character_count(selected) <= 180
    assert all(item.get("_evidence_id") for item in selected)


def test_short_draft_constraints_reject_long_output():
    draft = {"question": " ".join(["word"] * 26), "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "ok", "used_evidence_ids": ["E1"]}
    assert validate_draft_constraints(draft, [{"_evidence_id": "E1"}])["valid"] is False


def _gemini_response(question="Which update is supported?"):
    payload = {"question": question, "options": ["Opposite the gradient", "Randomly", "By page number", "Not at all"], "correct_index": 0, "explanation": "The evidence supports the update direction.", "used_evidence_ids": ["E1"]}
    return httpx.Response(200, request=httpx.Request("POST", "https://example.test"), json={"candidates": [{"content": {"parts": [{"text": __import__('json').dumps(payload)}]}}]})


def test_gemini_503_retries_then_succeeds():
    responses = [httpx.Response(503, request=httpx.Request("POST", "https://example.test")), _gemini_response()]
    provider = GeminiProvider(api_key="test", max_retries=3, sleep_fn=lambda _: None, random_fn=lambda *_: 0, http_post=lambda url, **kwargs: responses.pop(0))
    draft = provider.generate_quiz_from_evidence({"label": "Gradient Descent"}, [{"_evidence_id": "E1", "text": "Gradient descent moves opposite the gradient."}], "easy")
    assert draft.correct_index == 0
    assert provider.last_request_metrics["attempt_count"] == 2
    assert provider.last_request_metrics["http_status"] == 200


def test_gemini_503_fails_after_three_attempts():
    provider = GeminiProvider(api_key="test", max_retries=3, sleep_fn=lambda _: None, random_fn=lambda *_: 0, http_post=lambda url, **kwargs: httpx.Response(503, request=httpx.Request("POST", "https://example.test")))
    try:
        provider.generate_quiz_from_evidence({"label": "Gradient Descent"}, [{"_evidence_id": "E1", "text": "Gradient descent moves opposite the gradient."}], "easy")
    except httpx.HTTPStatusError:
        assert provider.last_request_metrics["attempt_count"] == 3
        assert provider.last_request_metrics["http_status"] == 503
    else:
        raise AssertionError("expected HTTPStatusError")


def test_gemini_401_is_not_retried():
    calls = []
    def post(url, **kwargs):
        calls.append(1)
        return httpx.Response(401, request=httpx.Request("POST", "https://example.test"))
    provider = GeminiProvider(api_key="test", max_retries=3, sleep_fn=lambda _: None, http_post=post)
    try:
        provider.generate_quiz_from_evidence({"label": "Gradient Descent"}, [{"_evidence_id": "E1", "text": "Gradient descent moves opposite the gradient."}], "easy")
    except httpx.HTTPStatusError:
        assert len(calls) == 1
    else:
        raise AssertionError("expected HTTPStatusError")


def test_gemini_429_is_bounded_and_not_hammered():
    calls = []
    def post(url, **kwargs):
        calls.append(1)
        return httpx.Response(429, request=httpx.Request("POST", "https://example.test"), json={"error": {"status": "RESOURCE_EXHAUSTED"}})
    provider = GeminiProvider(api_key="test", max_retries=3, sleep_fn=lambda _: None, random_fn=lambda *_: 0, http_post=post)
    try:
        provider.generate_quiz_from_evidence({"label": "Gradient Descent"}, [{"_evidence_id": "E1", "text": "Gradient descent moves opposite the gradient."}], "easy")
    except RuntimeError as exc:
        assert str(exc) == "PROVIDER_RATE_LIMIT"
        assert len(calls) == 2
    else:
        raise AssertionError("expected ProviderRateLimitError")


def test_validated_quiz_is_cached_and_second_call_avoids_provider(tmp_path):
    cache = QuizCache(tmp_path / "quiz_cache.json")
    first_provider = FakeProvider(valid_draft())
    first = generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", first_provider, cache=cache)
    second_provider = FakeProvider(valid_draft())
    second = generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", second_provider, cache=cache)
    assert first.validation.passed is True
    assert second.generator_type == "gemini_cached"
    assert second_provider.calls == 0


def test_source_change_invalidates_cache(tmp_path):
    cache = QuizCache(tmp_path / "quiz_cache.json")
    generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", FakeProvider(valid_draft()), cache=cache)
    changed = graph("Gradient descent minimizes a loss function using parameter updates.")
    provider = FakeProvider(valid_draft())
    result = generate_grounded_quiz(changed, "lesson_pdf", "gradient_descent", "easy", provider, cache=cache)
    assert provider.calls == 1
    assert result.generator_type == "gemini_live"


def test_model_change_invalidates_cache(tmp_path):
    cache = QuizCache(tmp_path / "quiz_cache.json")
    first = FakeProvider(valid_draft())
    generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", first, cache=cache)
    second = FakeProvider(valid_draft())
    second.model = "different-model"
    generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", second, cache=cache)
    assert second.calls == 1


def test_invalid_quiz_is_not_cached(tmp_path):
    cache = QuizCache(tmp_path / "quiz_cache.json")
    invalid = valid_draft().model_copy(update={"question": " ".join(["too"] * 26)})
    result = generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", FakeProvider(invalid), cache=cache)
    assert result.decision == "VALIDATION_FAILED"
    provider = FakeProvider(valid_draft())
    generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", provider, cache=cache)
    assert provider.calls == 1


def test_optional_fallback_is_explicitly_marked(tmp_path):
    result = generate_grounded_quiz(graph(), "lesson_pdf", "gradient_descent", "easy", FakeProvider(error=RuntimeError("offline")), allow_deterministic_fallback=True, cache=QuizCache(tmp_path / "fallback-cache.json"))
    assert result.generator_type == "deterministic_fallback"
