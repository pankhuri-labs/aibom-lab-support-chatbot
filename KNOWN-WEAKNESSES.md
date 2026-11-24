# Known weaknesses (planted on purpose)

This app is a target for the [CS54 AI-BOM security lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). The weaknesses below are deliberate. IDs match the CS54 [threat model](https://github.com/pankhuri-labs/CaseStudies/blob/main/CS54-AI-BOM-and-AI-Security-Posture-Lab/docs/threat-model.md). Attack tests arrive in phase 3 and fixes in phase 6.

| ID | Weakness | Where | OWASP LLM 2025 |
| --- | --- | --- | --- |
| AT-01 | Retrieved help articles go into the prompt as trusted text, and one article carries a hidden instruction | `app/main.py` `answer()`, `docs/kb/returns-policy.md` | LLM01, LLM08 |
| AT-02 | Internal notes with personal data (synthetic) are indexed with the public help articles | `app/retriever.py` `load_articles()`, `docs/kb/customer-notes.md` | LLM02 |
| AT-03 | Model output is inserted into the web page without HTML encoding | `app/main.py` `chat()` | LLM05 |
| AT-04 | The system prompt holds something that must stay secret (a fake staff discount code) | `prompts/system.txt` | LLM07 |
| AT-05 | No authentication, rate limit or token budget on the chat API | `app/main.py` `api_chat()` | LLM10 |
