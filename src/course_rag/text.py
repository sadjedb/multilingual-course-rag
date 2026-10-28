"""Text normalisation for three languages that need very different handling.

Arabic is the demanding one: the same word can be written with or without short vowels
(تَعَلُّم / تعلم), with different alef forms (أ إ آ ا), and with ة or ه at the end, and the article
and some prepositions are glued to the word (والشبكة = و + ال + شبكة). Lexical search (BM25)
treats every variant as a different word unless they are folded together first.
"""

import re
import unicodedata

ARABIC_CHAR = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
LATIN_CHAR = re.compile(r"[A-Za-zÀ-ɏ]")
TASHKEEL = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")  # short vowels, shadda, sukun...
TATWEEL = "ـ"  # the stretching character: كـتـاب
CITATION_MARK = re.compile(r"[\[\]]\s*(?:\d+|[a-z]|note \d+|nb \d+|n \d+)\s*[\[\]]", re.IGNORECASE)

FRENCH_HINTS = {
    "le", "la", "les", "des", "est", "une", "dans", "pour", "que", "qui", "sur", "pas", "du", "au",
    "aux", "par", "avec", "sont", "quoi", "quel", "quelle", "quels", "quelles", "comment", "pourquoi",
    "qu'est-ce", "c'est", "d'un", "d'une", "l'", "ce", "cette", "ou", "entre", "elle", "il",
}
ENGLISH_HINTS = {
    "the", "is", "are", "of", "and", "what", "which", "how", "why", "does", "do", "in", "to", "for",
    "with", "a", "an", "that", "this", "it", "on", "between", "when", "who", "can",
}

STOPWORDS = {
    "en": {
        "the", "a", "an", "of", "and", "or", "in", "on", "at", "to", "for", "is", "are", "was", "were",
        "be", "been", "by", "with", "as", "that", "this", "these", "those", "it", "its", "from", "which",
        "what", "how", "why", "when", "who", "does", "do", "did", "can", "into", "than", "then", "there",
        "their", "they", "such", "also", "not", "but", "if", "so",
    },
    "fr": {
        "le", "la", "les", "l", "un", "une", "des", "de", "du", "d", "et", "ou", "en", "dans", "sur", "au",
        "aux", "a", "est", "sont", "pour", "par", "avec", "que", "qu", "qui", "quoi", "ce", "cette", "ces",
        "se", "sa", "son", "ses", "il", "elle", "ils", "elles", "on", "ne", "pas", "plus", "c", "s", "y",
        "quel", "quelle", "quels", "quelles", "comment", "pourquoi", "entre", "lors", "leur", "leurs",
    },
    "ar": {
        "في", "من", "على", "الى", "عن", "ان", "او", "ما", "هو", "هي", "هذا", "هذه", "ذلك", "تلك", "التي",
        "الذي", "الذين", "مع", "كان", "كانت", "لا", "لم", "لن", "قد", "ثم", "كل", "بين", "عند", "كما", "اي",
        "ماذا", "كيف", "لماذا", "متى", "هل", "يتم", "به", "بها", "له", "لها", "و", "ف", "ب", "ل", "ك",
    },
}
ALL_STOPWORDS = set().union(*STOPWORDS.values())
ARABIC_PREFIXES = ("وال", "بال", "كال", "فال", "لل", "ال")


def strip_arabic_diacritics(text: str) -> str:
    return TASHKEEL.sub("", text).replace(TATWEEL, "")


def normalize_arabic(text: str) -> str:
    text = strip_arabic_diacritics(text)
    text = re.sub("[إأآٱ]", "ا", text)
    return text.replace("ى", "ي").replace("ة", "ه")


def fold_accents(text: str) -> str:
    """é -> e, ç -> c. Applied after Arabic normalisation so no Arabic letter loses information."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def detect_language(text: str) -> str:
    """Good enough for routing a question: Arabic by script, then French vs English by function words."""
    n_ar, n_lat = len(ARABIC_CHAR.findall(text)), len(LATIN_CHAR.findall(text))
    if n_ar > 0.3 * max(1, n_ar + n_lat):
        return "ar"
    words = re.findall(r"[a-zà-ÿ']+", text.lower())
    fr = sum(w in FRENCH_HINTS for w in words) + 2 * len(re.findall(r"[éèêàùçôîâ]", text.lower()))
    en = sum(w in ENGLISH_HINTS for w in words)
    return "fr" if fr > en else "en"


def light_arabic_stem(token: str) -> str:
    for prefix in ARABIC_PREFIXES:
        if token.startswith(prefix) and len(token) - len(prefix) >= 2:
            return token[len(prefix):]
    return token


def bm25_tokenize(text: str) -> list[str]:
    """Lowercase, fold Arabic variants and Latin accents, drop stopwords, strip the Arabic article."""
    text = fold_accents(normalize_arabic(text.lower()))
    tokens = re.findall(r"\w+", text)
    out = []
    for tok in tokens:
        if tok in ALL_STOPWORDS:
            continue
        if ARABIC_CHAR.match(tok):
            tok = light_arabic_stem(tok)
        out.append(tok)
    return out


def normalize_for_match(text: str) -> str:
    """Canonical form used to find an evaluation evidence quote inside a chunk.

    Punctuation and spacing differences between the PDF and markdown versions of a text
    should not decide whether a chunk counts as relevant, so only letters and digits are kept.
    """
    text = fold_accents(normalize_arabic(text.lower()))
    text = CITATION_MARK.sub(" ", text)
    return " ".join(re.findall(r"\w+", text))


SENTENCE_END = re.compile(r"(?<=[.!?؟])\s+|\n+")


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_END.split(text) if s and s.strip()]
