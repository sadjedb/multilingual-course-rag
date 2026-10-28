"""Load the raw course documents, clean them, and cut them into chunks.

Chunks are cut inside a section, never across two, and each one starts with a short header
("Document title > Section"). That header is cheap context: a chunk that only says "it is
decremented each time a process takes a resource" is much easier to retrieve once it also
says "Sémaphore (informatique) > Fonctionnement".
"""

import json
import re
from dataclasses import dataclass, field

import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from course_rag.config import CHUNK_OVERLAP, CHUNK_SIZE, CHUNKS_PATH, DOCS_PATH, MANIFEST_PATH, RAW_DIR
from course_rag.pdf import extract_pdf
from course_rag.text import CITATION_MARK, fold_accents, normalize_arabic

# Sections that hold links and bibliographies rather than course content.
DROP_SECTIONS = {
    "see also", "references", "notes", "further reading", "external links", "bibliography", "sources",
    "citations", "footnotes", "notes and references", "works cited",
    "voir aussi", "references", "notes et references", "bibliographie", "liens externes",
    "articles connexes", "liens internes", "annexes",
    "انظر ايضا", "المراجع", "مراجع", "وصلات خارجيه", "مصادر", "المصادر", "ملاحظات", "قراءات اضافيه",
    "روابط خارجيه", "مراجع وملاحظات", "اقرا ايضا",
}

DROP_KEYS = {re.sub(r"\W", "", k) for k in DROP_SECTIONS}

SEPARATORS = ["\n\n", "\n", ". ", "؟ ", "? ", "! ", "؛ ", "; ", "، ", ", ", " ", ""]


@dataclass
class Section:
    path: str  # "Heading > Subheading"
    body: str
    offset: int  # where the body starts in the extracted text (used to find the PDF page)


@dataclass
class CourseDocument:
    doc_id: str
    lang: str
    title: str
    course: str
    format: str
    url: str
    sections: list[Section] = field(default_factory=list)
    pdf: object = None  # PdfText for PDFs, used to map chunk offsets to page numbers

    @property
    def text(self) -> str:
        return "\n\n".join(f"## {s.path}\n{s.body}" if s.path else s.body for s in self.sections)


def _heading_key(heading: str) -> str:
    return re.sub(r"\W", "", fold_accents(normalize_arabic(heading.lower())))


DISPLAYSTYLE = re.compile(r"^\s*\{\\displaystyle\s*(.*)\}\s*$")
EDITOR_TAGS = re.compile(r"\[(?:réf\. (?:nécessaire|souhaitée)|lequel \?|quand \?|citation needed|clarification needed"
                         r"|which\?|when\?|by whom\?|according to whom\?|\?)\]", re.IGNORECASE)


def clean_wiki_math(text: str) -> str:
    """Wikipedia's plain-text export prints every formula as dozens of one-character lines (the
    rendered MathML) followed by its LaTeX source on a line like '{\\displaystyle f(x)}'.
    Keep only the LaTeX, inline, and glue the sentence back together around it."""
    out: list[str] = []
    pending: list[str] = []  # short lines that may turn out to be a formula's rendering
    after_math = False
    for line in text.split("\n"):
        m = DISPLAYSTYLE.match(line)
        if m:
            pending = []
            latex = m.group(1).strip().rstrip("\\,").strip()
            if out and out[-1].strip() and not out[-1].startswith("#"):
                out[-1] = out[-1].rstrip() + f" {latex}"
            else:
                out.append(latex)
            after_math = True
            continue
        stripped = line.strip()
        if after_math and not stripped:
            continue
        if after_math and (line[:1].isspace() or stripped[:1] in ",.;:)"):
            out[-1] += ("" if stripped[:1] in ",.;:)" else " ") + stripped  # the sentence continues after the formula
            after_math = False
            continue
        after_math = False
        if not stripped or (line[:1].isspace() and len(stripped) <= 8):  # the rendered formula is indented
            pending.append(line)
            continue
        out.extend(pending)
        pending = []
        out.append(line)
    out.extend(pending)
    return "\n".join(out)


def split_sections(text: str, title: str) -> list[Section]:
    """Split markdown-ish text at '#' headings and drop the reference/link sections."""
    sections, stack = [], []
    matches = list(re.finditer(r"^(#{1,6}) (.+)$", text, flags=re.MULTILINE))
    bounds = [(0, None, None)] + [(m.end(), len(m.group(1)), m.group(2).strip()) for m in matches]
    for i, (start, level, heading) in enumerate(bounds):
        end = matches[i].start() if i < len(matches) else len(text)
        if level is not None:
            if level == 1:
                stack = []  # the document title
            else:
                stack = [(lv, h) for lv, h in stack if lv < level] + [(level, heading)]
        if any(_heading_key(h) in DROP_KEYS for _, h in stack):
            continue
        raw = text[start:end]
        body = EDITOR_TAGS.sub("", CITATION_MARK.sub("", raw))
        body = re.sub(r"[ \t]+", " ", body)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        if body:
            lead = len(raw) - len(raw.lstrip())
            sections.append(Section(path=" > ".join(h for _, h in stack), body=body, offset=start + lead))
    return sections


def load_corpus(repair_rtl: bool = True) -> list[CourseDocument]:
    manifest = pd.read_csv(MANIFEST_PATH)
    docs = []
    for row in manifest.itertuples():
        path = RAW_DIR / row.path
        pdf = None
        if row.format == "pdf":
            pdf = extract_pdf(path, repair_rtl=repair_rtl)
            text = pdf.text
        else:
            text = clean_wiki_math(path.read_text(encoding="utf-8"))
        docs.append(CourseDocument(
            doc_id=row.doc_id, lang=row.lang, title=row.title, course=row.course, format=row.format,
            url=row.url, sections=split_sections(text, row.title), pdf=pdf,
        ))
    return docs


def chunk_documents(docs: list[CourseDocument], chunk_size: int = CHUNK_SIZE,
                    chunk_overlap: int = CHUNK_OVERLAP, min_chars: int = 60) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=SEPARATORS,
        keep_separator="end", add_start_index=True,
    )
    chunks = []
    for doc in docs:
        n = 0
        for section in doc.sections:
            for piece in splitter.create_documents([section.body]):
                body = piece.page_content.strip()
                if len(body) < min_chars:
                    continue
                header = f"{doc.title} > {section.path}" if section.path else doc.title
                page = doc.pdf.page_at(section.offset + piece.metadata["start_index"]) if doc.pdf else None
                chunks.append(Document(
                    page_content=f"{header}\n{body}",
                    metadata={
                        "chunk_id": f"{doc.doc_id}#{n:03d}", "doc_id": doc.doc_id, "lang": doc.lang,
                        "title": doc.title, "course": doc.course, "format": doc.format,
                        "section": section.path, "page": page, "url": doc.url, "body": body,
                    },
                ))
                n += 1
    return chunks


def save_corpus(docs: list[CourseDocument], chunks: list[Document]) -> None:
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps({"doc_id": d.doc_id, "lang": d.lang, "title": d.title, "course": d.course,
                                "format": d.format, "url": d.url, "text": d.text}, ensure_ascii=False) + "\n")
    save_chunks(chunks, CHUNKS_PATH)


def save_chunks(chunks: list[Document], path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({"text": c.page_content, **c.metadata}, ensure_ascii=False) + "\n")


def load_chunks(path=CHUNKS_PATH) -> list[Document]:
    chunks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            chunks.append(Document(page_content=row.pop("text"), metadata=row))
    return chunks


def load_documents(path=DOCS_PATH) -> dict[str, dict]:
    with open(path, encoding="utf-8") as f:
        return {d["doc_id"]: d for d in map(json.loads, f)}
