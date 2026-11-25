"""Model client. Ollama by default; the CS54 gateway (LLM_BACKEND=gateway, phase 7); a scripted
fake model for tests (LLM_BACKEND=fake)."""
import json
import os
import re
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("CHATBOT_MODEL", "llama3.2:3b")


def chat(system: str, user: str) -> str:
    backend = os.environ.get("LLM_BACKEND", "ollama")
    if backend == "fake":
        return _fake_model(system, user)
    if backend == "gateway":
        return gateway_chat([{"role": "system", "content": system}, {"role": "user", "content": user}])
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 300},  # PB-05 output cap
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["message"]["content"]


def gateway_chat(messages: list[dict]) -> str:
    """OpenAI-compatible call through the CS54 gateway, which checks the model against the AI-BOM,
    traces the call and enforces this app's key. GATEWAY_KEY is this app's own key, never a provider key."""
    payload = {"model": MODEL, "messages": messages, "temperature": 0.2, "max_tokens": 300}  # PB-05 output cap
    req = urllib.request.Request(
        f"{os.environ.get('GATEWAY_URL', 'http://localhost:4000')}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ['GATEWAY_KEY']}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


def _fake_model(system: str, user: str) -> str:
    """Behaves like a model with no defences: follows any instruction it finds in its input,
    otherwise answers from the first line of context after the article title."""
    hijack = re.search(r"ASSISTANT INSTRUCTION:(.+?)(?:-->|$)", user, re.S)
    if hijack:
        return " ".join(hijack.group(1).split())
    m = re.search(r"<article source='[^']+'>\n+(?:#.*\n+)?(.+)", user)
    return m.group(1).strip() if m else "I do not know. Please contact support."
