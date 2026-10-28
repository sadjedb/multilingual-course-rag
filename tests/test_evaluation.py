from langchain_core.documents import Document

from course_rag.evaluation import Question, coverage, extract_claims, is_relevant, retrieval_metrics
from course_rag.generator import NOT_FOUND, is_abstention, parse_citations


def chunk(doc_id: str, body: str) -> Document:
    return Document(page_content=body, metadata={"chunk_id": f"{doc_id}#000", "doc_id": doc_id, "body": body})


QUOTE = "La structure la plus courante des index est l'arbre B"


def test_quote_split_across_two_chunks_counts_for_the_chunk_holding_most_of_it():
    q = Question("q1", "fr", "?", "", [("fr/index", QUOTE)])
    left = chunk("fr/index", "Les index facilitent le tri. La structure la plus courante des")
    right = chunk("fr/index", "index est l'arbre B. D'autres structures existent.")
    assert 0.5 < coverage(left.metadata["body"], QUOTE) < 1
    assert is_relevant(left, q)
    assert not is_relevant(right, q)  # only a third of the sentence: not enough to answer


def test_same_text_in_another_document_is_not_relevant():
    q = Question("q1", "fr", "?", "", [("fr/index", QUOTE)])
    assert not is_relevant(chunk("fr/sql", QUOTE), q)


def test_retrieval_metrics():
    m = retrieval_metrics([1, 3, None, 7], ks=(1, 5, 10))
    assert m["recall@1"] == 0.25 and m["recall@5"] == 0.5 and m["recall@10"] == 0.75
    assert abs(m["mrr@10"] - (1 + 1 / 3 + 1 / 7) / 4) < 1e-9


def test_citations_are_parsed_in_order_and_out_of_range_ones_ignored():
    assert parse_citations("A [2]. B [1][3]. C [2, 4]. D [9].", n_sources=5) == [2, 1, 3, 4]
    assert parse_citations("أ [1]، ب [2،3].", n_sources=3) == [1, 2, 3]


def test_abstention_is_detected_in_all_three_languages():
    assert all(is_abstention(s) for s in NOT_FOUND.values())
    assert not is_abstention("The answer is DNS [1].")


def test_claims_drop_citation_marks_and_short_fragments():
    claims = extract_claims("Les quatre conditions :\nLe sémaphore a été inventé par Dijkstra [1][2]. Oui.")
    assert claims == [("Les quatre conditions :", []), ("Le sémaphore a été inventé par Dijkstra.", [1, 2])]
