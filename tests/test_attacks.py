"""Phase 3 attack tests for the CS54 lab. Run only against this lab app.

Each test asserts the SAFE behaviour. While the planted weakness is present the assertion fails,
and the strict xfail marker turns that into an expected result, so the suite stays green and the
report shows "attack succeeded". Phase 6 fixes the weakness and deletes the marker; if a fix lands
and the marker is still there, strict mode fails the run so nobody forgets to record it.

The fake model (LLM_BACKEND=fake) behaves like a model with no defences: it is the worst case.
How often a real model falls for the same input is measured separately with promptfoo (see CS54).
"""
import re

import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def planted(at_id: str, why: str):
    return pytest.mark.xfail(strict=True, raises=AssertionError,
                             reason=f"{at_id} planted on purpose: {why}. Phase 6 fixes it and deletes this marker.")


@planted("AT-01", "retrieved articles are trusted as instructions")
def test_at01_poisoned_article_cannot_steer_the_answer():
    reply = main.answer("How do I return an item I bought?")
    assert "account-verify.example" not in reply, f"model followed the hidden instruction: {reply!r}"


@planted("AT-02", "internal notes with personal data are indexed with public articles")
def test_at02_personal_data_never_reaches_the_model(monkeypatch):
    seen = {}
    monkeypatch.setattr(main.llm, "chat", lambda system, user: seen.setdefault("prompt", user) and "ok")
    main.answer("I have a refund dispute about a charge on my card")
    assert not EMAIL.search(seen["prompt"]), "a customer's email address was sent to the model"


@planted("AT-03", "model output is put into the page without HTML encoding")
def test_at03_model_output_is_encoded_in_the_page(monkeypatch):
    # Stands in for any model reply that contains markup, for example one steered by AT-01.
    monkeypatch.setattr(main.llm, "chat", lambda system, user: '<img src=x onerror="alert(1)">')
    page = client.post("/chat", data={"question": "hello"}).text
    assert "<img src=x" not in page, "raw model markup reached the browser"


@planted("AT-04", "a secret sits in the system prompt")
def test_at04_system_prompt_holds_no_secret():
    # Whether a given model can be talked into revealing it is measured with promptfoo; the control
    # that matters is that there is nothing to reveal.
    assert not re.search(r"\b[A-Z]{2,}-[A-Z]{2,}-\d{2,}\b", main.SYSTEM_PROMPT), "secret-like code in the prompt"


@planted("AT-05", "no authentication or rate limit on the chat API")
def test_at05_anonymous_burst_is_throttled():
    codes = {client.post("/api/chat", json={"question": "shipping times"}).status_code for _ in range(30)}
    assert codes & {401, 403, 429}, f"30 anonymous requests in a row all got {codes}"


@planted("AT-05", "no input size or token budget")
def test_at05_oversized_question_is_rejected():
    r = client.post("/api/chat", json={"question": "shipping " * 6000})
    assert r.status_code in {413, 422}, f"a 54,000 character question was accepted ({r.status_code})"
