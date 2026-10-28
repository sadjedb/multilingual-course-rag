"""Evaluation: is the right chunk retrieved, and is the answer grounded in what was retrieved?

Gold labels are evidence quotes, not chunk ids. A question says "the answer is in document D,
in the passage that contains this sentence". A chunk counts as relevant when it contains at
least half of that sentence (after normalisation). Because of that, the same labels work for
every chunk size and every cleaning tweak, which is what makes the chunk-size comparison fair.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher

import numpy as np
import pandas as pd
import torch
from langchain_core.documents import Document

from course_rag.config import EVAL_PATH, NLI_MODEL, device
from course_rag.generator import CITATION
from course_rag.text import normalize_for_match, split_sentences

KS = (1, 3, 5, 10)


@dataclass
class Question:
    qid: str
    q_lang: str
    question: str
    answer: str
    evidence: list[tuple[str, str]]  # (doc_id, quote) pairs; any one of them is enough

    @property
    def answerable(self) -> bool:
        return bool(self.evidence)

    @property
    def doc_lang(self) -> str | None:
        return self.evidence[0][0].split("/")[0] if self.evidence else None

    @property
    def kind(self) -> str:
        if not self.answerable:
            return "unanswerable"
        return "same-language" if self.q_lang == self.doc_lang else "cross-language"


def load_questions(path=EVAL_PATH) -> list[Question]:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    questions = []
    for r in df.itertuples():
        docs = [d.strip() for d in r.doc_id.split("||") if d.strip()]
        quotes = [q.strip() for q in r.evidence.split("||") if q.strip()]
        if len(docs) != len(quotes):
            raise ValueError(f"{r.qid}: {len(docs)} doc ids but {len(quotes)} evidence quotes")
        questions.append(Question(r.qid, r.q_lang, r.question, r.answer, list(zip(docs, quotes))))
    return questions


def coverage(chunk_text: str, quote: str) -> float:
    """Share of the (normalised) quote that appears in one piece inside the chunk."""
    a, b = normalize_for_match(chunk_text), normalize_for_match(quote)
    if not b:
        return 0.0
    if b in a:
        return 1.0
    match = SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return match.size / len(b)


def is_relevant(chunk: Document, question: Question, min_coverage: float = 0.5) -> bool:
    m = chunk.metadata
    return any(m["doc_id"] == doc and coverage(m["body"], quote) >= min_coverage for doc, quote in question.evidence)


def check_evidence(questions: list[Question], documents: dict[str, dict], chunks: list[Document]) -> list[str]:
    """Problems with the labels: a quote that isn't in its document, or that no chunk contains."""
    problems = []
    for q in questions:
        for doc, quote in q.evidence:
            if doc not in documents:
                problems.append(f"{q.qid}: unknown doc_id {doc!r}")
            elif normalize_for_match(quote) not in normalize_for_match(documents[doc]["text"]):
                problems.append(f"{q.qid}: evidence not found verbatim in {doc}: {quote[:60]!r}")
        if q.answerable and not any(is_relevant(c, q) for c in chunks if c.metadata["doc_id"] in dict(q.evidence)):
            problems.append(f"{q.qid}: no chunk covers the evidence")
    return problems


def first_relevant_rank(results: list[Document], question: Question) -> int | None:
    for rank, chunk in enumerate(results, start=1):
        if is_relevant(chunk, question):
            return rank
    return None


def retrieval_metrics(ranks: list[int | None], ks=KS) -> dict:
    """recall@k (here: share of questions with a relevant chunk in the top k) and MRR@max(k)."""
    n = len(ranks)
    out = {f"recall@{k}": sum(r is not None and r <= k for r in ranks) / n for k in ks}
    out[f"mrr@{max(ks)}"] = sum(1 / r for r in ranks if r is not None and r <= max(ks)) / n
    return out


def bootstrap_ci(values, n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=float)
    means = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


# ---------------------------------------------------------------- answer faithfulness

def strip_citations(text: str) -> str:
    return CITATION.sub("", text).replace(" .", ".").strip()


def windows(text: str, size: int = 3) -> list[str]:
    """Overlapping windows of `size` sentences. NLI models are trained on short premises,
    so a whole 1000-character chunk is split before it is used as a premise."""
    sents = split_sentences(text)
    if len(sents) <= size:
        return [" ".join(sents)] if sents else []
    return [" ".join(sents[i:i + size]) for i in range(len(sents) - size + 1)]


class NLIJudge:
    """Multilingual NLI model (mDeBERTa-v3, trained on NLI data in 27 languages, Arabic, French
    and English among them). A claim is supported if some passage window entails it."""

    def __init__(self, model_name: str = NLI_MODEL, threshold: float = 0.5, batch_size: int = 32):
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device()).eval()
        labels = {v.lower(): k for k, v in self.model.config.id2label.items()}
        self.entail_idx = labels["entailment"]
        self.threshold = threshold
        self.batch_size = batch_size

    @torch.inference_mode()
    def entailment(self, premises: list[str], hypotheses: list[str]) -> np.ndarray:
        probs = []
        for i in range(0, len(premises), self.batch_size):
            enc = self.tokenizer(premises[i:i + self.batch_size], hypotheses[i:i + self.batch_size],
                                 truncation="only_first", max_length=512, padding=True, return_tensors="pt")
            logits = self.model(**enc.to(self.model.device)).logits.float()
            probs.append(logits.softmax(-1)[:, self.entail_idx].cpu().numpy())
        return np.concatenate(probs) if probs else np.zeros(0)

    def support(self, claim: str, passages: list[str]) -> float:
        wins = [w for p in passages for w in windows(p)]
        if not wins:
            return 0.0
        return float(self.entailment(wins, [claim] * len(wins)).max())


LLM_SUPPORT_PROMPT = """Here are excerpts from course documents:

{excerpts}

Claim: {claim}

Is the claim fully supported by the excerpts? The claim and the excerpts may be written in different languages; judge the meaning. Answer with Yes or No."""


class LLMJudge:
    """The same Qwen model, asked claim by claim whether the excerpts support it.

    It reads cross-language pairs better than the NLI model, but it is the model that wrote
    the answers, so it may be lenient with its own phrasing. That's why both judges are reported.
    """

    def __init__(self, generator, threshold: float = 0.5):
        self.generator = generator
        self.threshold = threshold

    def support(self, claim: str, passages: list[str]) -> float:
        excerpts = "\n\n".join(f"[{i}] {p}" for i, p in enumerate(passages, start=1))
        prompt = LLM_SUPPORT_PROMPT.format(excerpts=excerpts, claim=claim)
        return self.generator.yes_probability([{"role": "user", "content": prompt}])


def extract_claims(answer: str) -> list[tuple[str, list[int]]]:
    """Answer sentences without their citation marks, with the excerpt numbers each one cites."""
    claims = []
    for sentence in split_sentences(answer):
        nums = [int(n) for group in CITATION.findall(sentence) for n in group.replace("،", ",").split(",")]
        claim = strip_citations(sentence)
        if len(claim.split()) >= 3:  # skips headers, list labels, "Yes."
            claims.append((claim, nums))
    return claims


def grounding(judge, answer: str, sources: list[str]) -> dict:
    """faithfulness: share of claims supported by the retrieved sources taken together.
    citation_precision: share of cited claims supported by the source(s) they cite."""
    scores, cite_ok = [], []
    for claim, nums in extract_claims(answer):
        scores.append(judge.support(claim, sources))
        valid = [n for n in nums if 1 <= n <= len(sources)]
        if valid:
            cite_ok.append(judge.support(claim, [sources[n - 1] for n in valid]) >= judge.threshold)
    return {
        "n_claims": len(scores),
        "faithfulness": float(np.mean([s >= judge.threshold for s in scores])) if scores else None,
        "citation_precision": float(np.mean(cite_ok)) if cite_ok else None,
        "claim_scores": [round(s, 3) for s in scores],
    }


# ---------------------------------------------------------------- answer correctness

JUDGE_PROMPT = """You are grading an answer to a university course question against a reference answer.

Question: {question}
Reference answer: {reference}
Answer to grade: {answer}

Is the answer to grade correct? It is CORRECT if it contains the key information of the reference answer and does not contradict it (extra correct details are fine, and the languages may differ). It is PARTIAL if it has only part of the key information. It is INCORRECT if it misses the key information, contradicts the reference, or says it could not find the answer.

Reply with one word: CORRECT, PARTIAL or INCORRECT."""


def judge_correctness(generator, question: str, reference: str, answer: str) -> str:
    reply = generator.chat([{"role": "user", "content": JUDGE_PROMPT.format(
        question=question, reference=reference, answer=strip_citations(answer))}], max_new_tokens=5)
    reply = reply.strip().upper()
    for label in ("INCORRECT", "PARTIAL", "CORRECT"):  # INCORRECT first: it contains "CORRECT"
        if label in reply:
            return label
    return "INCORRECT"
