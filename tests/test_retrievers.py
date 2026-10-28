from langchain_core.documents import Document

from course_rag.retrievers import BM25Retriever, HybridRetriever, RankedRetriever


def chunk(cid: str, text: str) -> Document:
    return Document(page_content=text, metadata={"chunk_id": cid})


class FixedRetriever(RankedRetriever):
    """Returns the same ranking for every query."""

    ranking: list[Document]

    def search(self, query: str, k: int) -> list[Document]:
        return self.ranking[:k]


def test_bm25_finds_the_matching_chunk_in_any_spelling():
    chunks = [chunk("a", "La mémoire virtuelle utilise la pagination."),
              chunk("b", "Le sémaphore protège une ressource."),
              chunk("c", "تستخدم الشبكة المحلية تقنية إيثرنت")]
    bm25 = BM25Retriever.from_documents(chunks)
    assert bm25.search("memoire virtuelle", 1)[0].metadata["chunk_id"] == "a"
    assert bm25.search("الشبكه", 1)[0].metadata["chunk_id"] == "c"  # article and ة/ه folded
    assert bm25.search("quantum chromodynamics", 3) == []


def test_rrf_rewards_agreement_between_retrievers():
    a, b, c = chunk("a", ""), chunk("b", ""), chunk("c", "")
    first = FixedRetriever(ranking=[a, b])
    second = FixedRetriever(ranking=[c, b])
    fused = HybridRetriever(retrievers=[first, second]).search("q", 3)
    # b is only 2nd in each list, but both lists have it: 2/62 beats a's and c's 1/61
    assert [d.metadata["chunk_id"] for d in fused] == ["b", "a", "c"]
    assert fused[0].metadata["rrf_score"] == 2 / 62


def test_rrf_weights():
    a, b = chunk("a", ""), chunk("b", "")
    fused = HybridRetriever(retrievers=[FixedRetriever(ranking=[a, b]), FixedRetriever(ranking=[b, a])],
                            weights=[1.0, 0.1]).search("q", 2)
    assert fused[0].metadata["chunk_id"] == "a"
