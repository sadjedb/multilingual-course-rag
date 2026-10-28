"""Embedding model, FAISS index, and one object that hands out every retrieval strategy."""

from pathlib import Path

import torch
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from course_rag.config import (CANDIDATES, CHUNK_SIZE, CHUNKS_PATH, EMBEDDING_MODEL, EMBEDDING_MODELS,
                               RERANKER_MODEL, TOP_K, index_path, model_device)
from course_rag.ingest import load_chunks
from course_rag.retrievers import BM25Retriever, DenseRetriever, HybridRetriever, RankedRetriever, RerankRetriever

MODES = ("bm25", "dense", "hybrid", "dense_rerank", "hybrid_rerank")


class SentenceTransformerEmbeddings(Embeddings):
    """LangChain wrapper around sentence-transformers that adds the query/passage prefixes
    some models (the e5 family) were trained with, and runs in fp16 on the GPU."""

    def __init__(self, model_name: str = EMBEDDING_MODEL, batch_size: int = 32, max_seq_length: int = 512):
        from sentence_transformers import SentenceTransformer

        dev = model_device("embedder")
        kwargs = {"dtype": torch.float16} if dev == "cuda" else {}
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=dev, model_kwargs=kwargs)
        self.model.max_seq_length = max_seq_length
        prefixes = EMBEDDING_MODELS.get(model_name, {})
        self.query_prefix = prefixes.get("query_prefix", "")
        self.doc_prefix = prefixes.get("doc_prefix", "")
        self.batch_size = batch_size

    def _encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, batch_size=self.batch_size, normalize_embeddings=True,
                                    convert_to_numpy=True, show_progress_bar=False)
        return vectors.astype("float32").tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode([self.doc_prefix + t for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._encode([self.query_prefix + text])[0]


def build_faiss(chunks: list[Document], embedder: Embeddings) -> FAISS:
    return FAISS.from_documents(chunks, embedder, ids=[c.metadata["chunk_id"] for c in chunks],
                                distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT)


def load_faiss(path: Path, embedder: Embeddings) -> FAISS:
    # The docstore is a pickle written by build_index.py on this machine, so loading it is safe.
    return FAISS.load_local(str(path), embedder, allow_dangerous_deserialization=True,
                            distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT)


def load_reranker(model_name: str = RERANKER_MODEL):
    from sentence_transformers import CrossEncoder

    dev = model_device("reranker")
    kwargs = {"dtype": torch.float16} if dev == "cuda" else {}
    return CrossEncoder(model_name, device=dev, max_length=512, model_kwargs=kwargs)


class SearchIndex:
    """The chunks plus everything built on them: BM25, the FAISS index and (optionally) the reranker."""

    def __init__(self, chunks: list[Document], vectorstore: FAISS, reranker=None):
        self.chunks = chunks
        self.vectorstore = vectorstore
        self.reranker = reranker
        self.bm25 = BM25Retriever.from_documents(chunks)
        self.dense = DenseRetriever(vectorstore=vectorstore)

    @classmethod
    def load(cls, embedding_model: str = EMBEDDING_MODEL, chunk_size: int = CHUNK_SIZE,
             with_reranker: bool = True, reranker=None, embedder: Embeddings | None = None) -> "SearchIndex":
        """Pass `reranker` / `embedder` to share already-loaded models between several indexes."""
        path = index_path(embedding_model, chunk_size)
        if not path.exists():
            raise FileNotFoundError(f"No index at {path}. Build it first: python -X utf8 scripts/build_index.py")
        chunks_path = CHUNKS_PATH if chunk_size == CHUNK_SIZE else path / "chunks.jsonl"
        embedder = embedder or SentenceTransformerEmbeddings(embedding_model)
        if with_reranker and reranker is None:
            reranker = load_reranker()
        return cls(load_chunks(chunks_path), load_faiss(path, embedder), reranker)

    def retriever(self, mode: str = "hybrid_rerank", k: int = TOP_K, candidates: int = CANDIDATES) -> RankedRetriever:
        if mode == "bm25":
            return self.bm25.model_copy(update={"k": k})
        if mode == "dense":
            return self.dense.model_copy(update={"k": k})
        hybrid = HybridRetriever(retrievers=[self.bm25, self.dense], candidates=candidates, k=k)
        if mode == "hybrid":
            return hybrid
        if self.reranker is None:
            raise ValueError(f"mode {mode!r} needs the reranker; load the index with with_reranker=True")
        if mode == "dense_rerank":
            return RerankRetriever(base=self.dense, model=self.reranker, candidates=candidates, k=k)
        if mode == "hybrid_rerank":
            return RerankRetriever(base=hybrid, model=self.reranker, candidates=candidates, k=k)
        raise ValueError(f"unknown mode {mode!r}, expected one of {MODES}")
