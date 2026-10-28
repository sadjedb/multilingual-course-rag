"""API smoke test in retrieval-only mode (no LLM, runs on CPU).

Needs the built index and downloads bge-m3 + the reranker on first run, so it is skipped
when the index hasn't been built (`python -X utf8 scripts/build_index.py`).
"""

import os

import pytest

from course_rag.config import index_path

pytestmark = pytest.mark.skipif(not index_path("BAAI/bge-m3").exists(), reason="index not built")


@pytest.fixture(scope="module")
def client():
    os.environ["COURSE_RAG_NO_LLM"] = "1"
    from fastapi.testclient import TestClient

    from course_rag.api import app

    with TestClient(app) as c:
        yield c


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["documents"] == 41 and body["generator"] is False


def test_search_crosses_languages(client):
    # French question, the answer is only in the Arabic course
    r = client.get("/search", params={"q": "À quoi sert le champ taille de la fenêtre dans l'en-tête TCP ?", "k": 3})
    assert r.status_code == 200
    results = r.json()["results"]
    assert results[0]["chunk_id"].startswith("ar/tcp")
    assert results[0]["page"] is not None  # a PDF source: citations carry the page


def test_ask_without_llm_is_unavailable(client):
    assert client.post("/ask", json={"question": "Qu'est-ce qu'un sémaphore ?"}).status_code == 503


def test_ask_validates_input(client):
    assert client.post("/ask", json={"question": "?"}).status_code == 422
    assert client.post("/ask", json={"question": "What is DNS?", "mode": "magic"}).status_code == 422
