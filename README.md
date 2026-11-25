# aibom-lab-support-chatbot

A small customer support chatbot that answers questions from help articles (retrieval-augmented generation) with **Llama 3.2 3B** running locally on Ollama.

> **Deliberately vulnerable lab app. Never deploy it or expose it beyond localhost.** It is one of four sample apps for the [CS54 AI-BOM and AI security posture lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). Its planted weaknesses, and the phase 6 fixes, are listed in [KNOWN-WEAKNESSES.md](KNOWN-WEAKNESSES.md).

## What it is, in AI-BOM terms

| AI-BOM field | Value |
| --- | --- |
| Model | `llama3.2:3b` (Meta Llama 3.2, 3B parameters) |
| Hosting | Local, Ollama on `localhost:11434` |
| Prompt | `prompts/system.txt` plus a user template in `app/main.py` |
| Sources | Customer question (untrusted); reviewed help articles in `docs/kb/public/`, listed with their SHA-256 in `MANIFEST.yaml` |
| Sinks | HTML page (`/chat`) and JSON API (`/api/chat`) |
| Tools | None |
| Exposure | Intended internet-facing; access key and rate limit on both chat endpoints since phase 6 (see `aibom.yaml`) |

## Run it on a Mac

1. Install Ollama: download the Mac app from [ollama.com/download](https://ollama.com/download), or run `brew install ollama`. Start it (open the app, or run `ollama serve`).
2. Pull the model (about 2 GB): `ollama pull llama3.2:3b`
3. Set up Python 3.11 or later:
   ```
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
   In `.env`, set `CHATBOT_API_KEY` to any long random value of your own (for example from `openssl rand -hex 16`).
4. Load the settings and start the app: `set -a; source .env; set +a; uvicorn app.main:app --port 8001`
5. Open http://localhost:8001, put your access key in the key box and ask, for example, "How do I reset my password?"

## Through the AI gateway (CS54 phase 7)

Set `LLM_BACKEND=gateway`, `GATEWAY_URL` and `GATEWAY_KEY` in your local `.env`. Every model call then goes through the lab's LiteLLM gateway, which checks this app's key, refuses any model its AI-BOM does not list, and writes a trace that the runtime monitor reads. The gateway and how to start it are in the CaseStudies repository, under `CS54-AI-BOM-and-AI-Security-Posture-Lab/gateway/`. The gateway key is made by that folder's `build_config.py`; keep it only in `.env`.

## Tests

The tests use a scripted fake model, so they need no Ollama and no key:

```
LLM_BACKEND=fake python -m pytest -q
```

The attack tests in `tests/test_attacks.py` assert the safe behaviour. In phase 3 they were expected failures, because the weaknesses were planted. Phase 6 fixed them, so they now pass and prove each fix holds. To see the attacks succeed, check out the last commit before the phase 6 fix PR and run `python -m pytest -q --runxfail tests/test_attacks.py`.

