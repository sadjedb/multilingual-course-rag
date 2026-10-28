"""Score every retrieval configuration on the labelled questions.

    python -X utf8 scripts/evaluate_retrieval.py

Three experiments, all on the same 98 answerable questions:
  1. retrieval strategy  (bge-m3, 1000-char chunks): bm25, dense, hybrid, dense_rerank, hybrid_rerank
  2. embedding model     (dense only): bge-m3 vs multilingual-e5-base vs English-only MiniLM
  3. chunk size          (bge-m3): 500 / 1000 / 1500 characters, dense and hybrid_rerank

Writes results/metrics/retrieval_per_question.csv (one row per question and config) and
results/metrics/retrieval.json (summary). Takes about 3 minutes on an RTX 5070.
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from course_rag.config import CHUNK_SIZE, EMBEDDING_MODEL, METRICS_DIR  # noqa: E402
from course_rag.evaluation import (KS, bootstrap_ci, first_relevant_rank, load_questions,  # noqa: E402
                                   retrieval_metrics)
from course_rag.index import MODES, SearchIndex, load_reranker  # noqa: E402

EXPERIMENTS = (
    [("strategy", EMBEDDING_MODEL, CHUNK_SIZE, mode) for mode in MODES]
    + [("embedder", m, CHUNK_SIZE, "dense") for m in ("intfloat/multilingual-e5-base",
                                                      "sentence-transformers/all-MiniLM-L6-v2")]
    + [("chunk_size", EMBEDDING_MODEL, size, mode) for size in (500, 1500) for mode in ("dense", "hybrid_rerank")]
)


def config_name(model: str, size: int, mode: str) -> str:
    return f"{mode} | {model.split('/')[-1]} | {size}"


def summarize(df: pd.DataFrame) -> dict:
    ranks = [None if pd.isna(r) else int(r) for r in df["rank"]]
    out = retrieval_metrics(ranks)
    out["recall@5_ci"] = bootstrap_ci([r is not None and r <= 5 for r in ranks])
    out["latency_ms"] = float(df["latency_ms"].median())
    out["n"] = len(df)
    return out


def main() -> None:
    questions = [q for q in load_questions() if q.answerable]
    reranker = load_reranker()
    indexes: dict = {}
    rows = []
    for experiment, model, size, mode in EXPERIMENTS:
        key = (model, size)
        if key not in indexes:
            shared = next((ix.vectorstore.embedding_function for (m, _), ix in indexes.items() if m == model), None)
            indexes[key] = SearchIndex.load(model, size, reranker=reranker, embedder=shared)
        retriever = indexes[key].retriever(mode, k=max(KS))
        retriever.search(questions[0].question, max(KS))  # warm-up, so the first latency isn't a cold start
        for q in questions:
            start = time.perf_counter()
            results = retriever.search(q.question, max(KS))
            latency = 1000 * (time.perf_counter() - start)
            rows.append({
                "experiment": experiment, "config": config_name(model, size, mode), "mode": mode,
                "embedder": model.split("/")[-1], "chunk_size": size, "qid": q.qid, "q_lang": q.q_lang,
                "doc_lang": q.doc_lang, "kind": q.kind, "rank": first_relevant_rank(results, q),
                "latency_ms": round(latency, 1), "top_chunks": " ".join(d.metadata["chunk_id"] for d in results[:3]),
            })
        done = pd.DataFrame([r for r in rows if r["config"] == config_name(model, size, mode)])
        s = summarize(done)
        print(f"{config_name(model, size, mode):45s} R@1 {s['recall@1']:.3f}  R@5 {s['recall@5']:.3f}  "
              f"R@10 {s['recall@10']:.3f}  MRR {s['mrr@10']:.3f}  {s['latency_ms']:.0f} ms", flush=True)

    df = pd.DataFrame(rows)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(METRICS_DIR / "retrieval_per_question.csv", index=False)

    summary = {}
    for config, g in df.groupby("config", sort=False):
        summary[config] = {
            "overall": summarize(g),
            "by_kind": {k: summarize(x) for k, x in g.groupby("kind")},
            "by_question_language": {k: summarize(x) for k, x in g.groupby("q_lang")},
            "by_document_language": {k: summarize(x) for k, x in g.groupby("doc_lang")},
        }
    (METRICS_DIR / "retrieval.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n-> {METRICS_DIR / 'retrieval.json'}")


if __name__ == "__main__":
    main()
