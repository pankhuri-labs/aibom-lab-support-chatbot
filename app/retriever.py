"""Keyword retriever over the help articles. No embeddings, to keep the lab light on an 8 GB laptop."""
import re
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "docs" / "kb"
_WORD = re.compile(r"[a-z]{3,}")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def load_articles(kb_dir: Path = KB_DIR) -> dict[str, str]:
    # Weakness: every file in the folder is indexed, including internal notes, and raw text
    # (HTML comments too) is kept. No provenance or trust label per document.
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(kb_dir.glob("*.md"))}


def search(question: str, articles: dict[str, str], k: int = 2) -> list[tuple[str, str]]:
    q = _tokens(question)
    scored = sorted(articles.items(), key=lambda kv: -len(q & _tokens(kv[1])))
    return [kv for kv in scored[:k] if q & _tokens(kv[1])]
