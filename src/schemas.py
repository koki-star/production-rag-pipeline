from typing import Literal

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    score: float
    source: Literal["internal_doc", "web"]
    url: str | None = None
    title: str | None = None
    stage1_rank: int | None = None
    stage2_rank: int | None = None


class RankShift(BaseModel):
    chunk_id: str
    stage1_rank: int | None = None
    stage2_rank: int | None = None


class RAGResponse(BaseModel):
    answer: str
    citations: list[str]
    route_taken: Literal["INTERNAL_RAG", "WEB_FALLBACK"]
    confidence_score: float
    transformed_query: str
    stage1_candidates: list[RetrievedChunk] = Field(default_factory=list)
    stage2_candidates: list[RetrievedChunk] = Field(default_factory=list)
    rank_shifts: list[RankShift] = Field(default_factory=list)
    gate_status: str = ""
