import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("LLM_BACKEND", "fake")
os.environ.setdefault("CHATBOT_API_KEY", "test-key-not-a-secret")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

KEY = os.environ["CHATBOT_API_KEY"]


@pytest.fixture(autouse=True)
def fresh_rate_limit():
    from app import main
    main._calls.clear()
    yield
