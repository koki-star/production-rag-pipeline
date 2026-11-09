"""Score candidate chunks with a cross-encoder and apply the confidence gate."""

from __future__ import annotations

import math

from src.schemas import RetrievedChunk

THRESHOLD = 0.55
K2 = 3
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model = None


def sigmoid(logit: float) -> float:
    """Map a raw model score to a number between 0 and 1."""
    value = float(logit)
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def confidence_from_logit(logit: float) -> float:
    """Normalize a raw cross-encoder logit so a 0.55 cutoff is meaningful."""
    score = sigmoid(logit)
    return min(1.0, max(0.0, score))


def gate_status(top_score: float, threshold: float = THRESHOLD) -> str:
    """Return LOW_CONFIDENCE or HIGH_CONFIDENCE from an already normalized score."""
    if top_score >= threshold:
        return "HIGH_CONFIDENCE"
    return "LOW_CONFIDENCE"


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder

        _model = CrossEncoder(CROSS_ENCODER_MODEL)
    return _model


def rerank(query: str, chunks: list[RetrievedChunk]) -> tuple[list[RetrievedChunk], float, str]:
    """Re-score Stage 1 chunks against the query and decide the confidence gate."""
    if not chunks:
        return [], 0.0, "LOW_CONFIDENCE"

    model = _get_model()
    pairs = [(query, chunk.content) for chunk in chunks]
    logits = model.predict(pairs)
    scored: list[RetrievedChunk] = []
    for index, (chunk, logit) in enumerate(zip(chunks, logits)):
        updated = chunk.model_copy(
            update={
                "score": confidence_from_logit(float(logit)),
                "stage1_rank": chunk.stage1_rank or (index + 1),
            }
        )
        scored.append(updated)

    scored.sort(key=lambda item: item.score, reverse=True)
    for rank, chunk in enumerate(scored, start=1):
        chunk.stage2_rank = rank

    top_confidence = scored[0].score
    return scored, top_confidence, gate_status(top_confidence)
