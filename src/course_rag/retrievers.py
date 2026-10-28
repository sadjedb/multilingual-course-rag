"""The four retrieval strategies compared in this project, as LangChain retrievers.

    BM25Retriever      lexical: matches the words of the question
    DenseRetriever     semantic: nearest chunks in a multilingual embedding space (FAISS)
    HybridRetriever    reciprocal rank fusion of several retrievers (here BM25 + dense)
    RerankRetriever    re-scores the candidates of another retriever with a cross-encoder

Each one has `search(query, k)`, which the evaluation uses directly, and LangChain's
`invoke(query)`, which returns the top `self.k`. Scores are added to a copy of each chunk's
metadata, so a result shows why it was ranked where it was.
"""

from abc import abstractmethod

import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict
from rank_bm25 import BM25Okapi

from course_rag.config import CANDIDATES, RRF_K, TOP_K
from course_rag.text import bm25_tokenize


def _with_scores(doc: Document, **scores: float) -> Document:
    return Document(page_content=doc.page_content, metadata={**doc.metadata, **scores})


class RankedRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    k: int = TOP_K

    @abstractmethod
    def search(self, query: str, k: int) -> list[Document]: ...

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        return self.search(query, self.k)


class BM25Retriever(RankedRetriever):
    chunks: list[Document]
    bm25: BM25Okapi

    @classmethod
    def from_documents(cls, chunks: list[Document], **kwargs) -> "BM25Retriever":
        return cls(chunks=chunks, bm25=BM25Okapi([bm25_tokenize(c.page_content) for c in chunks]), **kwargs)

    def search(self, query: str, k: int) -> list[Document]:
        scores = self.bm25.get_scores(bm25_tokenize(query))
        top = np.argsort(-scores)[:k]
        return [_with_scores(self.chunks[i], bm25_score=float(scores[i])) for i in top if scores[i] > 0]


class DenseRetriever(RankedRetriever):
    vectorstore: FAISS

    def search(self, query: str, k: int) -> list[Document]:
        hits = self.vectorstore.similarity_search_with_score(query, k=k)
        # Vectors are L2-normalised and the index uses inner product, so the score is the cosine similarity.
        return [_with_scores(doc, dense_score=float(score)) for doc, score in hits]


class HybridRetriever(RankedRetriever):
    """Reciprocal rank fusion: score(chunk) = sum over retrievers of weight / (rrf_k + rank).

    RRF only looks at ranks, so it doesn't matter that BM25 scores are unbounded while
    cosine similarities live in [-1, 1]. A chunk ranked well by both lists wins.
    """

    retrievers: list[RankedRetriever]
    weights: list[float] | None = None
    candidates: int = CANDIDATES
    rrf_k: int = RRF_K

    def search(self, query: str, k: int) -> list[Document]:
        weights = self.weights or [1.0] * len(self.retrievers)
        fused: dict[str, float] = {}
        docs: dict[str, Document] = {}
        for retriever, weight in zip(self.retrievers, weights):
            for rank, doc in enumerate(retriever.search(query, self.candidates), start=1):
                cid = doc.metadata["chunk_id"]
                fused[cid] = fused.get(cid, 0.0) + weight / (self.rrf_k + rank)
                docs[cid] = _with_scores(docs[cid], **doc.metadata) if cid in docs else doc
        best = sorted(fused, key=fused.get, reverse=True)[:k]
        return [_with_scores(docs[cid], rrf_score=fused[cid]) for cid in best]


class RerankRetriever(RankedRetriever):
    """Second stage: a cross-encoder reads (question, chunk) together and scores their relevance.

    Much more accurate than comparing two independent embeddings, but it has to run once per
    candidate, so it only re-orders the `candidates` best chunks of a cheaper first stage.
    """

    base: RankedRetriever
    model: object  # sentence_transformers.CrossEncoder
    candidates: int = CANDIDATES
    batch_size: int = 16

    def search(self, query: str, k: int) -> list[Document]:
        pool = self.base.search(query, self.candidates)
        if not pool:
            return []
        scores = self.model.predict([(query, d.page_content) for d in pool], batch_size=self.batch_size,
                                    show_progress_bar=False)
        order = np.argsort(-np.asarray(scores))[:k]
        return [_with_scores(pool[i], rerank_score=float(scores[i])) for i in order]
