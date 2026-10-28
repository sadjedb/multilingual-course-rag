"""PDF to text, with a fix for right-to-left lines.

The problem: a PDF stores glyphs with positions, not sentences. For Arabic lines that mix in
Latin words, e.g. «تعلم الآلة (بالإنجليزية: Machine Learning) هو أحد فروع ...», PyMuPDF returns
the direction runs in the wrong order:

    الذكاء  هو أحد فروع)Machine Learning :الإنجليزية( تع ّلم الآلة

The words survive, but the sentence is scrambled, which hurts both the embeddings and what the
LLM reads. The repair works on characters and their x positions: for a right-to-left block, sort
the characters of each line from right to left (that is reading order for Arabic) and then flip
each run of Latin letters/digits back, since those read left to right inside the Arabic sentence.

Two smaller fixes: drop the short-vowel marks (and the fake spaces PyMuPDF inserts in front of
some of them), and skip text set smaller than the body font (image captions, infobox tables).
"""

import re
import statistics
from dataclasses import dataclass

import pymupdf

from course_rag.text import ARABIC_CHAR, CITATION_MARK, LATIN_CHAR, TASHKEEL

LTR_CHAR = re.compile(r"[A-Za-z0-9À-ɏ]")


@dataclass
class PdfText:
    text: str
    page_starts: list[int]  # character offset in `text` where each page begins

    def page_at(self, offset: int) -> int:
        """1-based page number of the character at `offset`."""
        page = 1
        for i, start in enumerate(self.page_starts):
            if start <= offset:
                page = i + 1
        return page


def _drop_diacritics(chars: list[dict]) -> list[dict]:
    """Remove short-vowel marks and the fake spaces that come with them.

    Chrome sometimes gives a letter+vowel cluster a zero-width box and reports the cluster's
    advance as a separate space, so «تعلّم» comes out as «تع ّلم». Such a fake space starts exactly
    where the vowel mark sits; a real word gap does not.

    This doesn't catch every case («م ضيفين» for «مضيفين» survives). Broader rules I tried fixed
    those words but removed more real spaces elsewhere, so overall extraction quality went down.
    """
    out: list[dict] = []
    for ch in chars:
        if TASHKEEL.match(ch["c"]):
            tolerance = 0.05 * (ch["bbox"][3] - ch["bbox"][1])
            if out and out[-1]["c"] == " " and abs(out[-1]["bbox"][0] - ch["bbox"][0]) < tolerance:
                out.pop()
            continue
        out.append(ch)
    return out


def _rtl_line(chars: list[dict]) -> str:
    visual = sorted(chars, key=lambda ch: -(ch["bbox"][0] + ch["bbox"][2]) / 2)
    cs = [ch["c"] for ch in visual]
    out, i = [], 0
    while i < len(cs):
        if LTR_CHAR.match(cs[i]):
            # extend the run over Latin chars and the neutrals between them (spaces, ':', '.')
            end = k = i
            while k < len(cs) and not ARABIC_CHAR.match(cs[k]):
                if LTR_CHAR.match(cs[k]):
                    end = k
                k += 1
            out.extend(reversed(cs[i:end + 1]))
            i = end + 1
        else:
            out.append(cs[i])
            i += 1
    return "".join(out)


def _join_lines(lines: list[str]) -> str:
    text = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not text:
            text = line
        elif text.endswith("-"):
            text += line  # Chrome does not hyphenate, so a trailing '-' is a real hyphen: keep it, no space
        else:
            text += " " + line
    return text


def _is_rtl(text: str) -> bool:
    n_ar, n_lat = len(ARABIC_CHAR.findall(text)), len(LATIN_CHAR.findall(text))
    return n_ar > 0.3 * max(1, n_ar + n_lat)


def extract_pdf(path, repair_rtl: bool = True, skip_small_text: bool = True) -> PdfText:
    """Return the PDF as markdown-ish text: '#'/'##' headings, one paragraph per block.

    With repair_rtl=False this is plain PyMuPDF extraction, kept for comparison in notebook 01.
    """
    doc = pymupdf.open(path)
    pages = [page.get_text("rawdict") for page in doc]
    sizes = [
        round(span["size"], 1)
        for page in pages for block in page["blocks"] for line in block.get("lines", [])
        for span in line["spans"] for _ in span["chars"]
    ]
    body_size = statistics.mode(sizes)

    paragraphs: list[tuple[int, str, int]] = []  # (page, text, heading level or 0)
    for page_no, page in enumerate(pages, start=1):
        for block in page["blocks"]:
            lines = block.get("lines", [])
            if not lines:
                continue
            spans = [span for line in lines for span in line["spans"]]
            max_size = max(span["size"] for span in spans)
            raw = "".join(ch["c"] for span in spans for ch in span["chars"])
            if not raw.strip() or (skip_small_text and max_size < 0.92 * body_size):
                continue
            # Headings are bold and bigger than the body; a formula line has a few big glyphs but is not bold.
            visible = [(span, ch) for span in spans for ch in span["chars"] if not ch["c"].isspace()]
            mean_size = sum(span["size"] for span, _ in visible) / max(1, len(visible))
            all_bold = all(span["flags"] & 16 for span, _ in visible)
            level = 0
            if all_bold and mean_size > 1.15 * body_size:
                level = 2 if mean_size >= 1.4 * body_size else 3

            if repair_rtl and _is_rtl(raw):
                text = _join_lines([_rtl_line(_drop_diacritics([ch for s in l["spans"] for ch in s["chars"]])) for l in lines])
            else:
                text = _join_lines(["".join(ch["c"] for s in l["spans"] for ch in s["chars"]) for l in lines])

            text = re.sub(r"\s{2,}", " ", CITATION_MARK.sub("", text)).strip()
            if text:
                paragraphs.append((page_no, text, level if len(text) < 150 else 0))

    # Blocks often break mid-sentence (at page ends, around figures). Glue a block to the previous
    # one when the previous one does not end a sentence.
    parts: list[str] = []
    page_starts = [0] * len(pages)
    seen_page = 0
    offset = 0
    first_heading = True
    for page_no, text, level in paragraphs:
        if level:
            piece = "#" * (1 if first_heading else level) + " " + text
            first_heading = False
            sep = "\n\n"
        else:
            piece = text
            prev = parts[-1] if parts else ""
            continues = prev and not prev.startswith("#") and not re.search(r"[.!?؟:;)»\"]$", prev)
            sep = " " if continues else "\n\n"
        if parts:
            parts.append(sep)
            offset += len(sep)
        while seen_page < page_no:
            page_starts[seen_page] = offset
            seen_page += 1
        parts.append(piece)
        offset += len(piece)
    for p in range(seen_page, len(pages)):
        page_starts[p] = offset

    return PdfText(text="".join(parts), page_starts=page_starts)
