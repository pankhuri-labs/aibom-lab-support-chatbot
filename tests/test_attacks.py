"""Phase 3 attack tests for the CS54 lab. Run only against this lab app.

Each test asserts the SAFE behaviour. In phase 3 every one failed, because the weakness was planted,
and carried a strict expected-failure marker. Phase 6 fixed the weaknesses (CS54 PB-01 to PB-05) and
removed the markers, so these tests are now the proof that each fix holds.

Phase 6 also made the attacker an authorised user where the endpoint now needs a key: otherwise a
test would pass because the request was refused at the door, not because the control under test held.

The fake model (LLM_BACKEND=fake) behaves like a model with no defences: it is the worst case.
How often a real model falls for the same input is measured separately with promptfoo (see CS54).
"""
import re

from fastapi.testclient import TestClient

from app import main
from conftest import KEY

client = TestClient(main.app)
AUTH = {"X-API-Key": KEY}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")



def test_at01_poisoned_article_cannot_steer_the_answer():
    reply = main.answer("How do I return an item I bought?")
    assert "account-verify.example" not in reply, f"model followed the hidden instruction: {reply!r}"


def test_at02_personal_data_never_reaches_the_model(monkeypatch):
    seen = {}
    monkeypatch.setattr(main.llm, "chat", lambda system, user: seen.setdefault("prompt", user) and "ok")
    main.answer("I have a refund dispute about a charge on my card")
    assert not EMAIL.search(seen["prompt"]), "a customer's email address was sent to the model"


def test_at03_model_output_is_encoded_in_the_page(monkeypatch):
    # Stands in for any model reply that contains markup, for example one steered by AT-01.
    monkeypatch.setattr(main.llm, "chat", lambda system, user: '<img src=x onerror="alert(1)">')
    r = client.post("/chat", data={"question": "hello", "api_key": KEY})
    assert r.status_code == 200, "the attack must reach the page, not be refused at the door"
    page = r.text
    assert "<img src=x" not in page, "raw model markup reached the browser"


def test_at04_system_prompt_holds_no_secret():
    # Whether a given model can be talked into revealing it is measured with promptfoo; the control
    # that matters is that there is nothing to reveal.
    assert not re.search(r"\b[A-Z]{2,}-[A-Z]{2,}-\d{2,}\b", main.SYSTEM_PROMPT), "secret-like code in the prompt"


def test_at05_anonymous_burst_is_throttled():
    codes = {client.post("/api/chat", json={"question": "shipping times"}).status_code for _ in range(30)}
    assert codes & {401, 403, 429}, f"30 anonymous requests in a row all got {codes}"


def test_at05_oversized_question_is_rejected():
    r = client.post("/api/chat", json={"question": "shipping " * 6000})
    assert r.status_code in {413, 422}, f"a 54,000 character question was accepted ({r.status_code})"


def test_at05_signed_in_client_is_rate_limited():
    codes = [client.post("/api/chat", json={"question": "shipping times"}, headers=AUTH).status_code for _ in range(15)]
    assert codes[0] == 200 and 429 in codes, f"15 requests from one signed-in client got {set(codes)}"


def test_at01_visible_instruction_with_a_foreign_link_is_still_blocked(monkeypatch):
    # Defence in depth: even if an instruction got past ingest, the answer filter refuses foreign links.
    monkeypatch.setattr(main.llm, "chat", lambda s, u: "Verify your card at http://account-verify.example now.")
    assert "account-verify.example" not in main.answer("How do I return an item?")
