# aibom-lab-support-chatbot

A small customer support chatbot that answers questions from help articles (retrieval-augmented generation) with **Llama 3.2 3B** running locally on Ollama.

> **Deliberately vulnerable lab app. Never deploy it or expose it beyond localhost.** It is one of four sample apps for the [CS54 AI-BOM and AI security posture lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). Its planted weaknesses are listed in [KNOWN-WEAKNESSES.md](KNOWN-WEAKNESSES.md).

## What it is, in AI-BOM terms

| AI-BOM field | Value |
| --- | --- |
| Model | `llama3.2:3b` (Meta Llama 3.2, 3B parameters) |
| Hosting | Local, Ollama on `localhost:11434` |
| Prompt | `prompts/system.txt` plus a user template in `app/main.py` |
| Sources | Customer question (untrusted); help articles in `docs/kb/` (retrieved, should be semi-trusted) |
| Sinks | HTML page (`/chat`) and JSON API (`/api/chat`) |
| Tools | None |
| Exposure | Intended internet-facing, no authentication (see `aibom.yaml`) |

## Run it on a Mac

1. Install Ollama: download the Mac app from [ollama.com/download](https://ollama.com/download), or run `brew install ollama`. Start it (open the app, or run `ollama serve`).
2. Pull the model (about 2 GB): `ollama pull llama3.2:3b`
3. Set up Python 3.11 or later:
   ```
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
4. Start the app: `uvicorn app.main:app --port 8001`
5. Open http://localhost:8001 and ask, for example, "How do I reset my password?"

## Tests

The tests use a scripted fake model, so they need no Ollama and no key:

```
LLM_BACKEND=fake python -m pytest -q
```
