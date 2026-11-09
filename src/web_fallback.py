"""Search the public web when internal docs look too weak."""

from __future__ import annotations

import time
import warnings

from src.schemas import RetrievedChunk

# DuckDuckGo is first. Other backends are backups if DuckDuckGo returns nothing.
_BACKENDS = ("duckduckgo", "google", "brave", "bing", "wikipedia", "yahoo")


def _ddgs_client():
    try:
        from ddgs import DDGS

        return DDGS()
    except Exception:
        from duckduckgo_search import DDGS

        return DDGS()


def _fetch_raw(query: str, max_results: int, backend: str | None) -> list[dict]:
    client = None
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="This package .* renamed to")
            client = _ddgs_client()
        kwargs = {"max_results": max_results}
        if backend:
            kwargs["backend"] = backend
        return list(client.text(query, **kwargs))
    except TypeError:
        try:
            return list(client.text(query, max_results=max_results))
        except Exception:
            return []
    except Exception:
        return []
    finally:
        close = getattr(client, "close", None) if client is not None else None
        if callable(close):
            close()


def search_web(query: str, max_results: int = 3) -> list[RetrievedChunk]:
    """Return the top web snippets as RetrievedChunk objects with real URLs."""
    if not query.strip():
        return []

    raw_items: list[dict] = []
    for attempt in range(3):
        for backend in _BACKENDS:
            raw_items = _fetch_raw(query, max_results, backend)
            if raw_items:
                break
        if raw_items:
            break
        time.sleep(1.2 * (attempt + 1))

    chunks: list[RetrievedChunk] = []
    for index, item in enumerate(raw_items[:max_results], start=1):
        url = item.get("href") or item.get("url") or item.get("link") or ""
        title = item.get("title") or ""
        body = item.get("body") or item.get("snippet") or item.get("description") or ""
        content = ". ".join(part for part in [title, body] if part)
        if not url and not content:
            continue
        chunks.append(
            RetrievedChunk(
                chunk_id=f"web-{index}",
                content=content,
                score=0.0,
                source="web",
                url=url or None,
                title=title or None,
            )
        )
    return chunks
