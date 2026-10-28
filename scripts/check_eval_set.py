"""Validate data/eval/questions.csv and write a review sheet for checking it by hand.

    python -X utf8 scripts/check_eval_set.py

It fails if an evidence quote is not found word for word in its document (after normalisation),
or if no chunk covers it. It also writes data/eval/review.md, which shows every question next to
the passage(s) that hold its evidence, so the labels can be checked without opening the PDFs.
When you've checked a question, put "yes" in its `verified` column of the CSV, plus anything
worth knowing in `notes`.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from course_rag.config import EVAL_PATH  # noqa: E402
from course_rag.evaluation import check_evidence, is_relevant, load_questions  # noqa: E402
from course_rag.ingest import load_chunks, load_documents  # noqa: E402

REVIEW_PATH = EVAL_PATH.parent / "review.md"


def main() -> None:
    questions = load_questions()
    chunks = load_chunks()
    problems = check_evidence(questions, load_documents(), chunks)

    kinds = Counter(q.kind for q in questions)
    pairs = Counter(f"{q.q_lang}->{q.doc_lang}" for q in questions if q.answerable)
    print(f"{len(questions)} questions: " + ", ".join(f"{v} {k}" for k, v in kinds.items()))
    print("question language -> document language: " + ", ".join(f"{k} {v}" for k, v in sorted(pairs.items())))

    lines = ["# Evaluation set review", "",
             "Each question, its reference answer, and the chunk(s) that contain the evidence.",
             "Check that (1) the question is answerable from the passage, (2) the reference answer is right,",
             "(3) nothing else in the corpus would also answer it. Then mark `verified` = yes in questions.csv.", ""]
    for q in questions:
        lines += [f"## {q.qid} · {q.kind} · {q.q_lang} → {q.doc_lang or '-'}", "", f"**Q:** {q.question}", ""]
        if not q.answerable:
            lines += ["_Should be answered with \"not found\"._", ""]
            continue
        lines += [f"**Reference answer:** {q.answer}", ""]
        for doc, quote in q.evidence:
            lines += [f"**Evidence** ({doc}): «{quote}»", ""]
        for c in chunks:
            if c.metadata["doc_id"] in dict(q.evidence) and is_relevant(c, q):
                page = f", p. {c.metadata['page']}" if c.metadata.get("page") else ""
                lines += [f"<details><summary>{c.metadata['chunk_id']}{page}</summary>", "",
                          c.metadata["body"].replace("\n", "  \n"), "", "</details>", ""]
    REVIEW_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"review sheet -> {REVIEW_PATH}")

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("all evidence quotes found")


if __name__ == "__main__":
    main()
