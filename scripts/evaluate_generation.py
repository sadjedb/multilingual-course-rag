"""Generate answers for every labelled question and score them.

    python -X utf8 scripts/evaluate_generation.py

Configurations (all give the LLM the top 5 chunks, except closed_book which gives it nothing):
    closed_book     no retrieval: what Qwen3-4B knows on its own
    bm25            lexical retrieval only
    dense           bge-m3 + FAISS
    hybrid_rerank   BM25 + dense fused with RRF, re-ordered by the cross-encoder (the API default)

Scores per answer:
    correctness         CORRECT / PARTIAL / INCORRECT against the reference answer (LLM judge)
    faithfulness        share of answer sentences supported by the retrieved chunks
    citation_precision  share of cited sentences supported by the chunk(s) they cite
                        both measured twice: by a multilingual NLI model (nli_*) and by the LLM (llm_*)
    abstained           the model said the fixed "not found" sentence

The models don't all fit in 12 GB at once, so it runs in stages (retrieval -> generation and
judging -> NLI), and every stage saves its output and resumes where it stopped.
About 75 minutes on an RTX 5070, nearly all of it generation.
"""

import gc
import json
import sys
from pathlib import Path

import pandas as pd
import torch
from langchain_core.documents import Document
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from course_rag.config import GENERATION_DIR, METRICS_DIR, TOP_K  # noqa: E402
from course_rag.evaluation import (LLMJudge, NLIJudge, bootstrap_ci, grounding, is_relevant,  # noqa: E402
                                   judge_correctness, load_questions)
from course_rag.generator import Generator, is_abstention, parse_citations  # noqa: E402

CONFIGS = ["closed_book", "bm25", "dense", "hybrid_rerank"]
RETRIEVED = GENERATION_DIR / "retrieved.json"
ANSWERS = GENERATION_DIR / "answers.jsonl"
SCORED = GENERATION_DIR / "answers_scored.csv"


def free_gpu() -> None:
    gc.collect()
    torch.cuda.empty_cache()


def stage_retrieve(questions) -> dict:
    if RETRIEVED.exists():
        return json.loads(RETRIEVED.read_text(encoding="utf-8"))
    from course_rag.index import SearchIndex

    index = SearchIndex.load()
    out = {}
    for config in CONFIGS[1:]:
        retriever = index.retriever(config, k=TOP_K)
        out[config] = {q.qid: [{"page_content": d.page_content, "metadata": d.metadata} for d in retriever.invoke(q.question)]
                       for q in tqdm(questions, desc=f"retrieve {config}")}
    RETRIEVED.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    del index
    free_gpu()
    return out


def stage_generate(questions, retrieved) -> list[dict]:
    done = {}
    if ANSWERS.exists():
        for line in ANSWERS.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            done[(row["config"], row["qid"])] = row
    todo = [(c, q) for c in CONFIGS for q in questions if (c, q.qid) not in done]
    if todo:
        generator = Generator()
        llm_judge = LLMJudge(generator)
        with open(ANSWERS, "a", encoding="utf-8") as f:
            for config, q in tqdm(todo, desc="generate + judge"):
                chunks = [Document(**d) for d in retrieved.get(config, {}).get(q.qid, [])]
                answer = (generator.answer_closed_book(q.question, q.q_lang) if config == "closed_book"
                          else generator.answer(q.question, chunks, q.q_lang))
                row = {
                    "config": config, "qid": q.qid, "answer": answer, "abstained": is_abstention(answer),
                    "cited": parse_citations(answer, len(chunks)),
                    "correctness": judge_correctness(generator, q.question, q.answer, answer) if q.answerable else None,
                }
                if chunks and not row["abstained"]:
                    g = grounding(llm_judge, answer, [c.metadata["body"] for c in chunks])
                    row.update({f"llm_{k}": v for k, v in g.items()})
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                done[(config, q.qid)] = row
        del generator
        free_gpu()
    return list(done.values())


def stage_score(questions, retrieved, answers) -> pd.DataFrame:
    qmap = {q.qid: q for q in questions}
    nli = NLIJudge()
    rows = []
    for a in tqdm(answers, desc="NLI"):
        q = qmap[a["qid"]]
        chunks = [Document(**d) for d in retrieved.get(a["config"], {}).get(a["qid"], [])]
        row = {**a, "q_lang": q.q_lang, "doc_lang": q.doc_lang, "kind": q.kind,
               "retrieval_hit@5": any(is_relevant(c, q) for c in chunks) if q.answerable and chunks else None,
               "top_rerank_score": chunks[0].metadata.get("rerank_score") if chunks else None,
               "retrieved": " ".join(c.metadata["chunk_id"] for c in chunks)}
        if chunks and not a["abstained"]:
            g = grounding(nli, a["answer"], [c.metadata["body"] for c in chunks])
            row.update({f"nli_{k}": v for k, v in g.items()})
        rows.append(row)
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> dict:
    ans, unans = df[df.kind != "unanswerable"], df[df.kind == "unanswerable"]
    correct = (ans.correctness == "CORRECT").astype(float)
    out = {
        "n_answerable": len(ans),
        "correct": correct.mean(),
        "correct_ci": bootstrap_ci(correct),
        "correct_or_partial": ans.correctness.isin(["CORRECT", "PARTIAL"]).mean(),
        "false_abstention": ans.abstained.mean(),  # answerable but the model said "not found"
        "abstention_on_unanswerable": unans.abstained.mean() if len(unans) else None,
    }
    answered = df[~df.abstained & df.nli_faithfulness.notna()] if "nli_faithfulness" in df else df.iloc[0:0]
    if len(answered):
        for judge in ("nli", "llm"):
            out[f"{judge}_faithfulness"] = answered[f"{judge}_faithfulness"].mean()
            out[f"{judge}_faithfulness_ci"] = bootstrap_ci(answered[f"{judge}_faithfulness"].dropna())
            out[f"{judge}_fully_faithful_answers"] = (answered[f"{judge}_faithfulness"] == 1).mean()
            out[f"{judge}_citation_precision"] = answered[f"{judge}_citation_precision"].dropna().mean()
        out["answers_with_citations"] = (answered.cited.apply(len) > 0).mean()
    return out


def main() -> None:
    GENERATION_DIR.mkdir(parents=True, exist_ok=True)
    questions = load_questions()
    retrieved = stage_retrieve(questions)
    answers = stage_generate(questions, retrieved)
    df = stage_score(questions, retrieved, answers)
    df.to_csv(SCORED, index=False)

    summary = {}
    for config in CONFIGS:
        g = df[df.config == config]
        summary[config] = {"overall": summarize(g), "by_kind": {k: summarize(x) for k, x in g.groupby("kind") if k != "unanswerable"},
                           "by_question_language": {k: summarize(x) for k, x in g.groupby("q_lang")}}
        s = summary[config]["overall"]
        faith = (f"faithful nli {s['nli_faithfulness']:.3f} / llm {s['llm_faithfulness']:.3f}  "
                 f"cite-prec nli {s['nli_citation_precision']:.3f} / llm {s['llm_citation_precision']:.3f}"
                 if "nli_faithfulness" in s else "")
        print(f"{config:14s} correct {s['correct']:.3f}  (+partial {s['correct_or_partial']:.3f})  "
              f"false-abstain {s['false_abstention']:.3f}  abstain-on-unanswerable {s['abstention_on_unanswerable']:.3f}  {faith}")
    (METRICS_DIR / "generation.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    print(f"\n-> {SCORED}\n-> {METRICS_DIR / 'generation.json'}")


if __name__ == "__main__":
    main()
