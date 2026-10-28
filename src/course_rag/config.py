"""Paths and default settings shared by the scripts, the notebooks and the API."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
REFERENCE_TEXT_DIR = DATA_DIR / "reference_text"  # clean text of the PDF docs, only used to measure extraction quality
PROCESSED_DIR = DATA_DIR / "processed"
CHUNKS_PATH = PROCESSED_DIR / "chunks.jsonl"
DOCS_PATH = PROCESSED_DIR / "documents.jsonl"
MANIFEST_PATH = RAW_DIR / "manifest.csv"
TOPICS_PATH = DATA_DIR / "topics.csv"
EVAL_PATH = DATA_DIR / "eval" / "questions.csv"

INDEX_DIR = ROOT / "index"
RESULTS_DIR = ROOT / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
FIGURES_DIR = RESULTS_DIR / "figures"
GENERATION_DIR = RESULTS_DIR / "generation"

LANGS = ("ar", "fr", "en")
LANG_NAMES = {"ar": "Arabic", "fr": "French", "en": "English"}

# Chunking. Characters, not tokens: the three languages tokenize very differently,
# and characters keep chunk boundaries identical whichever embedding model is used.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Models. bge-m3 and bge-reranker-v2-m3 were trained on 100+ languages, including Arabic and French.
EMBEDDING_MODEL = os.getenv("COURSE_RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
RERANKER_MODEL = os.getenv("COURSE_RAG_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
GENERATOR_MODEL = os.getenv("COURSE_RAG_GENERATOR_MODEL", "Qwen/Qwen3-4B-Instruct-2507")
NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

# Embedding models compared in the retrieval notebook. Prefixes are what each model was trained with.
EMBEDDING_MODELS = {
    "BAAI/bge-m3": {"query_prefix": "", "doc_prefix": ""},
    "intfloat/multilingual-e5-base": {"query_prefix": "query: ", "doc_prefix": "passage: "},
    "sentence-transformers/all-MiniLM-L6-v2": {"query_prefix": "", "doc_prefix": ""},  # English-only baseline
}

# Retrieval defaults
TOP_K = 5  # chunks given to the LLM
CANDIDATES = 30  # chunks each first-stage retriever passes to fusion / reranking
RRF_K = 60  # the usual constant from Cormack et al. (2009)


def device() -> str:
    forced = os.getenv("COURSE_RAG_DEVICE")
    if forced:
        return forced
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def model_device(component: str) -> str:
    """Device for "embedder" or "reranker", overridable with COURSE_RAG_EMBEDDER_DEVICE / COURSE_RAG_RERANKER_DEVICE.

    On a 12 GB card, Qwen (8 GB) + bge-m3 + the reranker (2.2 GB) + what the desktop uses overflow VRAM;
    Windows then spills into system RAM and everything gets many times slower. Moving the embedder to
    the CPU costs ~0.1 s per question and avoids that (the API does this by default, see api.py)."""
    return os.getenv(f"COURSE_RAG_{component.upper()}_DEVICE") or device()


def index_path(embedding_model: str, chunk_size: int = CHUNK_SIZE) -> Path:
    slug = embedding_model.split("/")[-1].lower()
    return INDEX_DIR / f"{slug}_c{chunk_size}"
