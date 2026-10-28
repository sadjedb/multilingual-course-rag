"""Turn data/raw into chunks and FAISS indexes.

    python -X utf8 scripts/build_index.py                      # chunks + bge-m3 index (what the API uses)
    python -X utf8 scripts/build_index.py --all-models         # also the comparison embedders
    python -X utf8 scripts/build_index.py --chunk-sizes 500 1500  # extra chunk sizes for the ablation

Only the default chunk size is written to data/processed/; the ablation chunk sets are kept
next to their index under index/.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from course_rag.config import CHUNK_SIZE, EMBEDDING_MODEL, EMBEDDING_MODELS, index_path  # noqa: E402
from course_rag.index import SentenceTransformerEmbeddings, build_faiss  # noqa: E402
from course_rag.ingest import chunk_documents, load_corpus, save_chunks, save_corpus  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-models", action="store_true", help="index with every model in EMBEDDING_MODELS")
    parser.add_argument("--chunk-sizes", type=int, nargs="*", default=[],
                        help="extra chunk sizes, indexed with the default embedder")
    args = parser.parse_args()

    docs = load_corpus()
    chunks = chunk_documents(docs)
    save_corpus(docs, chunks)
    print(f"{len(docs)} documents, {len(chunks)} chunks of ~{CHUNK_SIZE} characters")

    jobs = [(m, CHUNK_SIZE) for m in (EMBEDDING_MODELS if args.all_models else [EMBEDDING_MODEL])]
    jobs += [(EMBEDDING_MODEL, size) for size in args.chunk_sizes if size != CHUNK_SIZE]

    embedders = {}
    for model, size in jobs:
        embedder = embedders.setdefault(model, SentenceTransformerEmbeddings(model))
        cs = chunks if size == CHUNK_SIZE else chunk_documents(docs, chunk_size=size, chunk_overlap=size * 15 // 100)
        start = time.perf_counter()
        store = build_faiss(cs, embedder)
        out = index_path(model, size)
        store.save_local(str(out))
        if size != CHUNK_SIZE:
            save_chunks(cs, out / "chunks.jsonl")
        print(f"{model:45s} chunk={size:5d}  {len(cs):5d} chunks  {time.perf_counter() - start:6.1f}s  -> {out}")


if __name__ == "__main__":
    main()
