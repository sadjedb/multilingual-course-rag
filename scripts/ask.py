"""Ask the assistant from the terminal.

    python -X utf8 scripts/ask.py "Qu'est-ce qu'un sémaphore ?"
    python -X utf8 scripts/ask.py                       # interactive: type a question, Enter, repeat
    python -X utf8 scripts/ask.py --no-llm "What is DNS?"   # only show what would be retrieved
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from course_rag.index import MODES, SearchIndex  # noqa: E402
from course_rag.pipeline import RAGPipeline, to_source  # noqa: E402


def show_source(s) -> str:
    page = f", p. {s.page}" if s.page else ""
    section = f" > {s.section}" if s.section else ""
    return f"  [{s.n}] {s.title}{section} ({s.lang}{page})  score {s.score:.3f}\n      {s.snippet[:160]}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("questions", nargs="*")
    p.add_argument("--mode", default="hybrid_rerank", choices=MODES)
    p.add_argument("-k", type=int, default=5)
    p.add_argument("--no-llm", action="store_true", help="retrieval only")
    args = p.parse_args()

    generator = None
    if not args.no_llm:
        os.environ.setdefault("COURSE_RAG_EMBEDDER_DEVICE", "cpu")  # leave the GPU to the LLM, see api.py
        from course_rag.generator import Generator

        generator = Generator()
    rag = RAGPipeline(SearchIndex.load(), generator, mode=args.mode, k=args.k)

    def handle(question: str) -> None:
        if args.no_llm:
            for i, c in enumerate(rag.retrieve(question), start=1):
                print(show_source(to_source(i, c)))
            return
        r = rag.ask(question)
        print(f"\n{r.answer}\n")
        for s in r.citations or r.sources:
            print(show_source(s))
        print(f"  ({r.language}, retrieval {r.timings_ms['retrieval']} ms, generation {r.timings_ms['generation']} ms)")

    if args.questions:
        for q in args.questions:
            print(f"\n> {q}")
            handle(q)
    else:
        while True:
            try:
                q = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if q:
                handle(q)


if __name__ == "__main__":
    main()
