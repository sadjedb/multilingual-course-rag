"""Answer generation with a local LLM (Qwen3-4B-Instruct) and citation parsing.

The model sees the retrieved chunks as numbered excerpts and must put [n] after every sentence.
When the excerpts don't answer the question it must reply with one fixed sentence (NOT_FOUND),
which makes abstentions easy to detect in the evaluation.
"""

import re

import torch
from langchain_core.documents import Document

from course_rag.config import GENERATOR_MODEL, LANG_NAMES

NOT_FOUND = {
    "en": "I could not find this in the course documents.",
    "fr": "Je n'ai pas trouvé cette information dans les documents du cours.",
    "ar": "لم أجد هذه المعلومة في وثائق المقرر.",
}

SYSTEM_PROMPT = """You are a teaching assistant for university courses. You answer students' questions using only the course excerpts you are given.

Rules:
- Use only information stated in the excerpts. Do not add facts from your own knowledge.
- End every sentence with the number of the excerpt(s) it comes from, like [1] or [2][3].
- Write the answer in {language}, even when the excerpts are in another language. You may keep a technical term in its original language in parentheses.
- Be concise: 2 to 5 sentences, or a short list if the question asks for several items.
- If the excerpts do not contain the answer, reply with exactly this sentence and nothing else: {not_found}"""

# Baseline without retrieval: what the model answers from its own memory.
CLOSED_BOOK_PROMPT = """You are a teaching assistant for university courses. Answer the student's question in {language}, in 2 to 5 sentences. If you do not know the answer, reply with exactly this sentence and nothing else: {not_found}"""

CITATION = re.compile(r"\[(\d+(?:\s*[,،]\s*\d+)*)\]")


def format_excerpts(chunks: list[Document]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        m = chunk.metadata
        where = m["title"] + (f" > {m['section']}" if m.get("section") else "")
        parts.append(f"[{i}] ({where}; {LANG_NAMES[m['lang']]})\n{m['body']}")
    return "\n\n".join(parts)


def build_messages(question: str, chunks: list[Document], lang: str) -> list[dict]:
    system = SYSTEM_PROMPT.format(language=LANG_NAMES[lang], not_found=NOT_FOUND[lang])
    user = f"Course excerpts:\n\n{format_excerpts(chunks)}\n\nQuestion: {question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_citations(answer: str, n_sources: int) -> list[int]:
    """Excerpt numbers cited in the answer, in order of first appearance, ignoring out-of-range ones."""
    seen = []
    for group in CITATION.findall(answer):
        for num in re.split(r"\s*[,،]\s*", group):
            n = int(num)
            if 1 <= n <= n_sources and n not in seen:
                seen.append(n)
    return seen


def is_abstention(answer: str) -> bool:
    text = answer.strip().rstrip(".").lower()
    return any(text.startswith(p.rstrip(".").lower()) for p in NOT_FOUND.values())


class Generator:
    def __init__(self, model_name: str = GENERATOR_MODEL, max_new_tokens: int = 400):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        self.model.eval()
        self.max_new_tokens = max_new_tokens

    @torch.inference_mode()
    def chat(self, messages: list[dict], max_new_tokens: int | None = None) -> str:
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        out = self.model.generate(**inputs, max_new_tokens=max_new_tokens or self.max_new_tokens, do_sample=False,
                                  temperature=None, top_p=None, top_k=None)
        return self.tokenizer.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    @torch.inference_mode()
    def yes_probability(self, messages: list[dict]) -> float:
        """P("Yes") / (P("Yes") + P("No")) for the first token of the reply. Reading the
        probabilities gives a graded score instead of parsing generated text."""
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        logits = self.model(**inputs, logits_to_keep=1).logits[0, -1].float()
        yes, no = (self.tokenizer.encode(w, add_special_tokens=False)[0] for w in ("Yes", "No"))
        return float(torch.softmax(logits[[yes, no]], dim=0)[0])

    def answer(self, question: str, chunks: list[Document], lang: str) -> str:
        return self.chat(build_messages(question, chunks, lang))

    def answer_closed_book(self, question: str, lang: str) -> str:
        system = CLOSED_BOOK_PROMPT.format(language=LANG_NAMES[lang], not_found=NOT_FOUND[lang])
        return self.chat([{"role": "system", "content": system}, {"role": "user", "content": question}])
