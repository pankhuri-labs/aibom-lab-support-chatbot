"""Functional tests with the fake model. Attack tests arrive in phase 3."""
from fastapi.testclient import TestClient

from app import retriever
from app.main import app

client = TestClient(app)


def test_home_page_loads():
    r = client.get("/")
    assert r.status_code == 200
    assert "Acme Gadgets support" in r.text


def test_retriever_finds_the_right_article():
    hits = retriever.search("how long does express shipping take", retriever.load_articles())
    assert hits[0][0] == "shipping.md"


def test_normal_question_gets_an_answer_from_the_article():
    r = client.post("/api/chat", json={"question": "How do I reset my password?"})
    assert r.status_code == 200
    assert "Forgot password" in r.json()["answer"]


def test_unknown_question_says_do_not_know():
    r = client.post("/api/chat", json={"question": "zzz qqq"})
    assert "do not know" in r.json()["answer"]
