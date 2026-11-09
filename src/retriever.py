"""Stage 1 retrieval: embed internal docs and search with a bi-encoder."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from src.schemas import RetrievedChunk

K1 = 20
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "internal_docs"

_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = _ROOT / "docs"
CHROMA_DIR = _ROOT / "data" / "chroma"
HASH_PATH = _ROOT / "data" / "corpus.hash"

_retriever = None


def _chunk_markdown(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"(?=^## )", text, flags=re.M)
    chunks: list[dict[str, str]] = []
    for index, part in enumerate(parts):
        content = part.strip()
        if len(content) < 40:
            continue
        heading = content.splitlines()[0].lstrip("# ").strip()
        chunks.append(
            {
                "chunk_id": f"{path.stem}-{index + 1}",
                "content": content,
                "title": heading or path.stem,
                "source_file": path.name,
            }
        )
    return chunks


def _load_corpus(docs_dir: Path) -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    for path in sorted(docs_dir.glob("*.md")):
        chunks.extend(_chunk_markdown(path))
    return chunks


def _corpus_hash(docs_dir: Path) -> str:
    joined = []
    for path in sorted(docs_dir.glob("*.md")):
        joined.append(path.name)
        joined.append(path.read_text(encoding="utf-8"))
    return hashlib.sha256("\n".join(joined).encode("utf-8")).hexdigest()


class Retriever:
    def __init__(self, docs_dir: Path | None = None, persist_dir: Path | None = None):
        self.docs_dir = Path(docs_dir) if docs_dir else DOCS_DIR
        self.persist_dir = Path(persist_dir) if persist_dir else CHROMA_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.hash_path = self.persist_dir.parent / "corpus.hash"
        from sentence_transformers import SentenceTransformer
        import chromadb

        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._sync_index()

    def _sync_index(self) -> None:
        current = _corpus_hash(self.docs_dir)
        stored = self.hash_path.read_text(encoding="utf-8").strip() if self.hash_path.exists() else ""
        if stored == current and self.collection.count() > 0:
            return

        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        chunks = _load_corpus(self.docs_dir)
        if not chunks:
            self.hash_path.write_text(current, encoding="utf-8")
            return

        embeddings = self.model.encode([item["content"] for item in chunks], normalize_embeddings=True)
        self.collection.add(
            ids=[item["chunk_id"] for item in chunks],
            documents=[item["content"] for item in chunks],
            metadatas=[
                {"title": item["title"], "source_file": item["source_file"]}
                for item in chunks
            ],
            embeddings=embeddings.tolist(),
        )
        self.hash_path.write_text(current, encoding="utf-8")

    def search(self, query: str, k: int = K1) -> list[RetrievedChunk]:
        if not query.strip() or self.collection.count() == 0:
            return []
        query_embedding = self.model.encode([query], normalize_embeddings=True).tolist()
        n_results = min(k, self.collection.count())
        raw = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        chunks: list[RetrievedChunk] = []
        ids = raw.get("ids", [[]])[0]
        documents = raw.get("documents", [[]])[0]
        distances = raw.get("distances", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        for rank, (chunk_id, content, distance, metadata) in enumerate(
            zip(ids, documents, distances, metadatas),
            start=1,
        ):
            similarity = 1.0 - float(distance)
            meta = metadata or {}
            chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    content=content,
                    score=similarity,
                    source="internal_doc",
                    title=meta.get("title"),
                    stage1_rank=rank,
                )
            )
        return chunks


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
