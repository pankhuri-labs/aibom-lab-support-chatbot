"""The gateway backend sends an OpenAI-compatible request with this app's own key (CS54 phase 7)."""
import io
import json

from app import llm


def test_gateway_backend_sends_model_cap_and_app_key(monkeypatch):
    sent = {}

    def fake_urlopen(req, timeout):
        sent.update(url=req.full_url, body=json.loads(req.data), auth=req.get_header("Authorization"))
        return io.BytesIO(json.dumps({"choices": [{"message": {"content": "Visit the returns page."}}]}).encode())

    monkeypatch.setenv("LLM_BACKEND", "gateway")
    monkeypatch.setenv("GATEWAY_URL", "http://gw.test")
    monkeypatch.setenv("GATEWAY_KEY", "sk-lab-test")
    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    assert llm.chat("system", "question") == "Visit the returns page."
    assert sent["url"] == "http://gw.test/chat/completions"
    assert sent["auth"] == "Bearer sk-lab-test"
    assert sent["body"]["model"] == llm.MODEL and sent["body"]["max_tokens"] == 300
