"""Keyword retriever over the help articles. No embeddings, to keep the lab light on an 8 GB laptop.

Phase 6 fixes (CS54 PB-01, PB-02): only reviewed articles listed in MANIFEST.yaml with a matching
SHA-256 are indexed; hidden text is stripped at ingest; personal data is redacted at ingest.
"""
import hashlib
import re
from pathlib import Path

import yaml

KB_DIR = Path(__file__).resolve().parent.parent / "docs" / "kb" / "public"
_WORD = re.compile(r"[a-z]{3,}")
HIDDEN = re.compile(r"<!--.*?-->", re.S)
PII = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d ]{8,}\d|card ending \d{4}", re.I)


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def clean(text: str) -> str:
    """What the model may read: the visible text only, with personal data redacted."""
    return PII.sub("[redacted]", HIDDEN.sub("", text)).strip()


def load_articles(kb_dir: Path = KB_DIR) -> dict[str, str]:
    manifest = yaml.safe_load((kb_dir / "MANIFEST.yaml").read_text())
    approved = {a["file"]: a["sha256"] for a in manifest["articles"]}
    articles = {}
    for p in sorted(kb_dir.glob("*.md")):
        raw = p.read_bytes()
        if approved.get(p.name) != hashlib.sha256(raw).hexdigest():
            continue  # not reviewed, or changed since review: never indexed
        articles[p.name] = clean(raw.decode("utf-8"))
    return articles


def search(question: str, articles: dict[str, str], k: int = 2) -> list[tuple[str, str]]:
    q = _tokens(question)
    scored = sorted(articles.items(), key=lambda kv: -len(q & _tokens(kv[1])))
    return [kv for kv in scored[:k] if q & _tokens(kv[1])]
