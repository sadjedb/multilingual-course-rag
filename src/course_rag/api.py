"""HTTP API.

    uvicorn course_rag.api:app --app-dir src --port 8000
    # then open http://localhost:8000/docs

Environment variables:
    COURSE_RAG_NO_LLM=1          retrieval only (/search works, /ask returns 503); no GPU needed
    COURSE_RAG_EMBEDDER_DEVICE   where the query embedder runs; defaults to "cpu" in the API
    COURSE_RAG_MIN_SCORE=0.01    answer "not found" without calling the LLM when the best reranked
                                 chunk scores below this. Off by default: notebook 03 shows that correct
                                 cross-language answers can score lower than off-topic questions, and
                                 the LLM's own "not found" was reliable on its own.
"""

import os
import threading
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from course_rag.config import TOP_K
from course_rag.ingest import load_documents
from course_rag.pipeline import RAGPipeline, to_source

Mode = Literal["bm25", "dense", "hybrid", "dense_rerank", "hybrid_rerank"]

state: dict = {}
gpu_lock = threading.Lock()  # one generation at a time; parallel requests would only fight over the GPU


@asynccontextmanager
async def lifespan(app: FastAPI):
    from course_rag.index import SearchIndex

    # Keep the GPU for the LLM and the reranker; one query embedding on the CPU costs ~0.1 s, while
    # overflowing a 12 GB card made every request ~10x slower (see config.model_device).
    os.environ.setdefault("COURSE_RAG_EMBEDDER_DEVICE", "cpu")

    generator = None
    if not os.getenv("COURSE_RAG_NO_LLM"):
        from course_rag.generator import Generator

        generator = Generator()
    min_score = float(os.environ["COURSE_RAG_MIN_SCORE"]) if os.getenv("COURSE_RAG_MIN_SCORE") else None
    state["rag"] = RAGPipeline(SearchIndex.load(), generator, min_rerank_score=min_score)
    state["documents"] = load_documents()
    yield
    state.clear()


app = FastAPI(
    title="Multilingual Course RAG",
    description="Questions in Arabic, French or English about course documents in any of the three; "
                "every answer cites the passages it is based on.",
    version="0.1.0",
    lifespan=lifespan,
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000,
                          examples=["Quelles sont les conditions d'un interblocage ?"])
    mode: Mode = "hybrid_rerank"
    k: int = Field(TOP_K, ge=1, le=10, description="number of chunks given to the LLM")


class SourceOut(BaseModel):
    n: int = Field(description="the [n] used in the answer")
    chunk_id: str
    title: str
    section: str
    page: int | None = Field(description="page in the PDF, null for text documents")
    lang: str
    url: str
    snippet: str
    score: float | None


class AskResponse(BaseModel):
    question: str
    language: str = Field(description="detected language of the question; the answer is written in it")
    answer: str
    abstained: bool = Field(description="true when the documents don't contain the answer")
    citations: list[SourceOut] = Field(description="the sources the answer cites")
    sources: list[SourceOut] = Field(description="every source that was given to the model")
    timings_ms: dict[str, int]


class SearchResponse(BaseModel):
    query: str
    mode: Mode
    results: list[SourceOut]


@app.get("/health")
def health() -> dict:
    rag: RAGPipeline = state["rag"]
    return {"status": "ok", "documents": len(state["documents"]), "chunks": len(rag.index.chunks),
            "generator": rag.generator is not None}


@app.get("/documents")
def documents() -> list[dict]:
    return [{k: d[k] for k in ("doc_id", "title", "lang", "course", "format", "url")} for d in state["documents"].values()]


@app.get("/search", response_model=SearchResponse)
def search(q: str = Query(..., min_length=2, max_length=1000), mode: Mode = "hybrid_rerank",
           k: int = Query(TOP_K, ge=1, le=20)) -> SearchResponse:
    """Retrieval only, no LLM: the chunks the assistant would read for this question."""
    chunks = state["rag"].retrieve(q, mode=mode, k=k)
    return SearchResponse(query=q, mode=mode, results=[SourceOut(**vars(to_source(i, c))) for i, c in enumerate(chunks, 1)])


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    rag: RAGPipeline = state["rag"]
    if rag.generator is None:
        raise HTTPException(503, "Started with COURSE_RAG_NO_LLM=1: only /search is available")
    with gpu_lock:
        result = rag.ask(req.question, mode=req.mode, k=req.k)
    return AskResponse(**result.to_dict())
