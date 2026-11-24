# Known weaknesses (planted on purpose, fixed in phase 6)

This app is a target for the [CS54 AI-BOM security lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). The weaknesses below are deliberate. IDs match the CS54 [threat model](https://github.com/pankhuri-labs/CaseStudies/blob/main/CS54-AI-BOM-and-AI-Security-Posture-Lab/docs/threat-model.md). Attack tests that prove each one are in `tests/test_attacks.py` (phase 3): they assert the safe behaviour and are marked as expected failures while the weakness is present. Phase 6 fixed them and removed the markers; the second table shows each fix.

| ID | Weakness | Where | OWASP LLM 2025 |
| --- | --- | --- | --- |
| AT-01 | Retrieved help articles go into the prompt as trusted text, and one article carries a hidden instruction | `app/main.py` `answer()`, `docs/kb/returns-policy.md` | LLM01, LLM08 |
| AT-02 | Internal notes with personal data (synthetic) are indexed with the public help articles | `app/retriever.py` `load_articles()`, `docs/kb/customer-notes.md` | LLM02 |
| AT-03 | Model output is inserted into the web page without HTML encoding | `app/main.py` `chat()` | LLM05 |
| AT-04 | The system prompt holds something that must stay secret (a fake staff discount code) | `prompts/system.txt` | LLM07 |
| AT-05 | No authentication, rate limit or token budget on the chat API | `app/main.py` `api_chat()` | LLM10 |

## Phase 6 fixes

Each fix follows a playbook in the CS54 remediation plan. A fix counts as closed only when its attack test passes **and** the AI-BOM rescan no longer raises the signal.

| ID | Playbook | Fix | Proof |
| --- | --- | --- | --- |
| AT-01 | PB-01 | Only reviewed articles listed in `docs/kb/public/MANIFEST.yaml` with a matching SHA-256 are indexed. Hidden text is stripped at ingest. Articles reach the model inside `<article>` tags marked as reference data. Answers that link to a host outside the allow-list are replaced with a safe reply. | `test_at01_poisoned_article_cannot_steer_the_answer`, `test_at01_visible_instruction_with_a_foreign_link_is_still_blocked` |
| AT-02 | PB-02 | Internal notes moved out of the corpus to `docs/internal/`. Contact details are redacted at ingest and again on the way out. | `test_at02_personal_data_never_reaches_the_model` |
| AT-03 | PB-03 | Question and answer are HTML-encoded, and a content security policy blocks script. | `test_at03_model_output_is_encoded_in_the_page` |
| AT-04 | PB-04 | The discount code is gone from the system prompt; anything secret belongs in a backend check the model cannot read. | `test_at04_system_prompt_holds_no_secret` |
| AT-05 | PB-05 | Both chat endpoints need an access key (`CHATBOT_API_KEY`), allow 10 questions a minute per key and client, reject questions over 2,000 characters, and cap the answer at 300 tokens. | the three `test_at05_*` tests |

The fake model obeys any instruction it reads, so these tests show the controls around the model hold even when the model does not. With Llama 3.2, run the promptfoo config in CS54 `attack-runner/real-model/` to see how often the model itself still follows the planted note.
