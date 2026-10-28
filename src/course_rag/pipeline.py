"""Question -> retrieved chunks -> answer with citations."""

import time
from dataclasses import asdict, dataclass, field

from langchain_core.documents import Document

from course_rag.config import TOP_K
from course_rag.generator import NOT_FOUND, Generator, is_abstention, parse_citations
from course_rag.index import SearchIndex
from course_rag.text import detect_language


@dataclass
class Source:
    n: int  # the [n] used in the answer
    chunk_id: str
    title: str
    section: str
    page: int | None
    lang: str
    url: str
    snippet: str
    score: float | None


@dataclass
class RAGAnswer:
    question: str
    language: str
    answer: str
    citations: list[Source]  # the sources the answer actually cites
    sources: list[Source]  # everything that was shown to the model
    abstained: bool
    timings_ms: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def to_source(n: int, chunk: Document) -> Source:
    m = chunk.metadata
    score = m.get("rerank_score", m.get("rrf_score", m.get("dense_score", m.get("bm25_score"))))
    body = m["body"]
    return Source(n=n, chunk_id=m["chunk_id"], title=m["title"], section=m.get("section", ""),
                  page=m.get("page"), lang=m["lang"], url=m["url"],
                  snippet=body if len(body) <= 300 else body[:300].rsplit(" ", 1)[0] + " …", score=score)


class RAGPipeline:
    """`min_rerank_score`: if the best reranked chunk scores below it, answer NOT_FOUND without
    calling the LLM at all. Off by default (None): reranker scores for cross-language pairs run
    so low that any threshold also refuses answerable questions (notebook 03), while the
    LLM's own "not found" caught every off-topic question in the evaluation."""

    def __init__(self, index: SearchIndex, generator: Generator | None, mode: str = "hybrid_rerank",
                 k: int = TOP_K, min_rerank_score: float | None = None):
        self.index = index
        self.generator = generator
        self.mode = mode
        self.k = k
        self.min_rerank_score = min_rerank_score

    def retrieve(self, question: str, mode: str | None = None, k: int | None = None) -> list[Document]:
        return self.index.retriever(mode or self.mode, k=k or self.k).invoke(question)

    def ask(self, question: str, mode: str | None = None, k: int | None = None) -> RAGAnswer:
        lang = detect_language(question)
        t0 = time.perf_counter()
        chunks = self.retrieve(question, mode, k)
        t1 = time.perf_counter()
        sources = [to_source(i, c) for i, c in enumerate(chunks, start=1)]

        top = chunks[0].metadata.get("rerank_score") if chunks else None
        if not chunks or (self.min_rerank_score is not None and top is not None and top < self.min_rerank_score):
            answer = NOT_FOUND[lang]
        elif self.generator is None:
            raise RuntimeError("this pipeline was built without a generator; use retrieve() instead")
        else:
            answer = self.generator.answer(question, chunks, lang)
        t2 = time.perf_counter()

        cited = parse_citations(answer, len(sources))
        return RAGAnswer(
            question=question, language=lang, answer=answer,
            citations=[sources[n - 1] for n in cited], sources=sources, abstained=is_abstention(answer),
            timings_ms={"retrieval": round(1000 * (t1 - t0)), "generation": round(1000 * (t2 - t1))},
        )
