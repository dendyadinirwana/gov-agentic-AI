#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_retrieval_config() -> dict[str, Any]:
    path = CONFIGS / "retrieval.generated.json"
    return load_json(path) if path.exists() else {"enabled": False}


def normalize(text: str) -> list[str]:
    return [token.strip().lower() for token in text.replace("_", " ").replace("-", " ").split() if token.strip()]


def load_corpus(config: dict[str, Any]) -> list[dict[str, Any]]:
    corpus_path = config.get("corpus_path")
    if not corpus_path:
        return []
    path = ROOT / corpus_path if not Path(corpus_path).is_absolute() else Path(corpus_path)
    return load_json(path) if path.exists() else []


def build_query_terms(request_text: str, intent_class: str | None, config: dict[str, Any]) -> list[str]:
    terms = normalize(request_text)
    if intent_class:
        terms.extend(normalize(intent_class))
        for hint in config.get("intent_queries", {}).get(intent_class, []):
            terms.extend(normalize(hint))
    out: list[str] = []
    for term in terms:
        if term not in out:
            out.append(term)
    return out


def score_document(doc: dict[str, Any], query_terms: list[str]) -> int:
    haystack = " ".join([
        doc.get("title", ""),
        doc.get("content", ""),
        " ".join(doc.get("tags", [])),
        doc.get("document_type", ""),
        doc.get("owner", ""),
    ]).lower()
    return sum(2 if term in haystack else 0 for term in query_terms)


def retrieve(request_text: str, intent_class: str | None = None, limit: int | None = None) -> dict[str, Any]:
    config = load_retrieval_config()
    if not config.get("enabled", False):
        return {"provider": "disabled", "query_terms": [], "hits": []}

    corpus = load_corpus(config)
    query_terms = build_query_terms(request_text, intent_class, config)
    scored = []
    for doc in corpus:
        score = score_document(doc, query_terms)
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)

    max_hits = limit or int(config.get("default_limit", 3))
    hits = []
    for score, doc in scored[:max_hits]:
        hit = {
            "score": score,
            "source_id": doc.get("source_id"),
            "title": doc.get("title"),
            "owner": doc.get("owner"),
            "document_type": doc.get("document_type"),
            "classification": doc.get("classification"),
            "issue_date": doc.get("issue_date"),
            "uri": doc.get("uri"),
            "excerpt": doc.get("content"),
            "tags": doc.get("tags", []),
        }
        hits.append(hit)

    return {
        "provider": config.get("provider", "local-json-corpus"),
        "query_terms": query_terms,
        "hits": hits,
    }
