"""Acme Gadgets support chatbot. DELIBERATELY VULNERABLE LAB APP: never deploy or expose it."""
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from app import llm, retriever

SYSTEM_PROMPT = (Path(__file__).resolve().parent.parent / "prompts" / "system.txt").read_text()
ARTICLES = retriever.load_articles()

app = FastAPI(title="Acme Gadgets support chatbot (lab)")

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Acme support</title></head>
<body style="font-family:sans-serif;max-width:40rem;margin:2rem auto">
<h1>Acme Gadgets support</h1>
<form method="post" action="/chat"><input name="question" style="width:80%" autofocus>
<button>Ask</button></form>{answer}</body></html>"""


def answer(question: str) -> str:
    hits = retriever.search(question, ARTICLES)
    context = "\n\n".join(f"### Article: {name}\n{text}" for name, text in hits)
    # Weakness: retrieved text is pasted straight into the prompt as if it were trusted.
    user = f"Help articles:\n{context}\n\nCustomer question: {question}"
    return llm.chat(SYSTEM_PROMPT, user)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return PAGE.format(answer="")


@app.post("/chat", response_class=HTMLResponse)
def chat(question: str = Form(...)) -> str:
    reply = answer(question)
    # Weakness: model output is inserted into the page without HTML encoding (AT-03).
    return PAGE.format(answer=f"<p><b>You:</b> {question}</p><div><b>Assistant:</b> {reply}</div>")


@app.post("/api/chat")
def api_chat(payload: dict) -> dict:
    # Weakness: no authentication, no rate limit, no token budget (AT-05).
    return {"answer": answer(str(payload.get("question", "")))}
