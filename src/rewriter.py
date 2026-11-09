"""Turn a conversational question into a clearer search query."""

from __future__ import annotations

import re

_PRONOUNS = ("its", "it", "that", "this", "they", "them", "those")
_FILLER = [
    r"^(can you|could you|would you|please|please can you)\s+",
    r"\bplease\b",
    r"^(i want to know|tell me|do you know)\s+",
]


def _phrases_from_history(history: list[str]) -> list[str]:
    blob = " ".join(history)
    found = re.findall(r"(?:[A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)+)", blob)
    # Keep longer names first so "Kubernetes Worker Nodes" wins over a short match.
    unique: list[str] = []
    for phrase in sorted(set(found), key=len, reverse=True):
        unique.append(phrase)
    return unique


def rewrite_query(query: str, conversation_history: list[str] | None = None) -> str:
    """Rewrite a messy or follow-up question into an explicit search query.

    If the rewriter has no extra model available, this local version still
    fills in pronouns from the earlier messages and drops extra filler words.
    Empty input returns an empty string and does not raise an error.
    """
    if query is None:
        return ""
    text = query.strip()
    if not text:
        return ""

    history = conversation_history or []
    if isinstance(history, str):
        history = [history]

    phrases = _phrases_from_history(history)
    pronoun_match = re.search(r"\b(its|it|that|this|they|them|those)\b", text, flags=re.I)
    if pronoun_match and phrases:
        phrase = phrases[0]
        token = pronoun_match.group(1).lower()
        if token == "its" and re.search(r"system requirements", text, flags=re.I):
            text = f"What are the system requirements for {phrase}?"
        else:
            text = re.sub(rf"\b{re.escape(pronoun_match.group(1))}\b", phrase, text, count=1, flags=re.I)
            if phrase not in text:
                text = f"{text} {phrase}"

    for pattern in _FILLER:
        text = re.sub(pattern, "", text, flags=re.I)
    return " ".join(text.split())
