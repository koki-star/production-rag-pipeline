"""Run the full two-stage RAG path, including the web fallback branch."""

from __future__ import annotations

from src.generator import generate_answer
from src.reranker import K2, rerank
from src.retriever import K1, get_retriever
from src.rewriter import rewrite_query
from src.schemas import RAGResponse, RankShift
from src.web_fallback import search_web


def run_pipeline(query: str, conversation_history: list[str] | None = None) -> RAGResponse:
    transformed = rewrite_query(query, conversation_history)
    if not transformed:
        transformed = (query or "").strip()

    retriever = get_retriever()
    stage1 = retriever.search(transformed, k=K1)
    stage2, confidence, status = rerank(transformed, stage1)

    if status == "HIGH_CONFIDENCE":
        selected = stage2[:K2]
        route = "INTERNAL_RAG"
    else:
        selected = search_web(transformed, max_results=3)
        route = "WEB_FALLBACK"

    response = generate_answer(
        query=transformed or query,
        chunks=selected,
        route_taken=route,
        confidence_score=confidence,
        transformed_query=transformed,
    )
    response.stage1_candidates = stage1
    response.stage2_candidates = stage2[:5]
    response.gate_status = status
    response.rank_shifts = [
        RankShift(
            chunk_id=chunk.chunk_id,
            stage1_rank=chunk.stage1_rank,
            stage2_rank=chunk.stage2_rank,
        )
        for chunk in response.stage2_candidates
    ]
    return response
