"""Download the course documents from Wikipedia.

Each topic in data/topics.csv is saved either as a PDF (rendered by Wikipedia) or as a
markdown "lecture note" made from the plain-text extract. For the PDF topics the plain text is
also saved to data/reference_text/, so notebook 01 can measure how much text the PDF
extraction loses or scrambles.

Everything is Wikipedia content under CC BY-SA 4.0; the manifest records the URL and revision
of every file so the attribution is complete.

    python -X utf8 scripts/fetch_corpus.py           # skips files that already exist
    python -X utf8 scripts/fetch_corpus.py --force   # downloads everything again
"""

import argparse
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from course_rag.config import MANIFEST_PATH, RAW_DIR, REFERENCE_TEXT_DIR, TOPICS_PATH  # noqa: E402

HEADERS = {"User-Agent": "multilingual-course-rag/0.1 (educational project; https://github.com/)"}


def get(url: str, **kwargs) -> requests.Response:
    """GET with backoff, because both Wikipedia endpoints answer 429 when called too fast."""
    for attempt in range(6):
        r = requests.get(url, headers=HEADERS, timeout=180, **kwargs)
        if r.status_code != 429:
            r.raise_for_status()
            return r
        time.sleep(int(r.headers.get("Retry-After", 10 * (attempt + 1))))
    r.raise_for_status()


def page_info(lang: str, title: str) -> dict:
    r = get(
        f"https://{lang}.wikipedia.org/w/api.php",
        params={
            "action": "query", "titles": title, "redirects": 1, "format": "json", "formatversion": 2,
            "prop": "extracts|revisions|info", "explaintext": 1, "exsectionformat": "wiki",
            "rvprop": "ids|timestamp", "inprop": "url",
        },
    )
    page = r.json()["query"]["pages"][0]
    if page.get("missing"):
        raise ValueError(f"{lang}:{title} does not exist")
    return page


def extract_to_markdown(title: str, extract: str) -> str:
    """TextExtracts marks sections as '== Heading ==' (more '=' for deeper levels); turn them into markdown."""

    def heading(m: re.Match) -> str:
        level = len(m.group(1))
        return "#" * level + " " + m.group(2).strip()

    body = re.sub(r"^(={2,6})\s*(.+?)\s*\1\s*$", heading, extract, flags=re.MULTILINE)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return f"# {title}\n\n{body.strip()}\n"


def download_pdf(lang: str, title: str) -> bytes:
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/pdf/{quote(title.replace(' ', '_'), safe='')}"
    content = get(url).content
    if content[:4] != b"%PDF":
        raise RuntimeError(f"{lang}:{title}: the PDF endpoint did not return a PDF")
    return content


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    topics = pd.read_csv(TOPICS_PATH)
    rows = []
    for t in topics.itertuples():
        out = RAW_DIR / t.lang / f"{t.slug}.{t.format}"
        out.parent.mkdir(parents=True, exist_ok=True)
        page = page_info(t.lang, t.title)
        md = extract_to_markdown(page["title"], page["extract"])

        if t.format == "md":
            if args.force or not out.exists():
                out.write_text(md, encoding="utf-8")
        else:
            ref = REFERENCE_TEXT_DIR / t.lang / f"{t.slug}.md"
            ref.parent.mkdir(parents=True, exist_ok=True)
            ref.write_text(md, encoding="utf-8")
            if args.force or not out.exists():
                out.write_bytes(download_pdf(t.lang, page["title"]))
                time.sleep(2)

        rows.append({
            "doc_id": f"{t.lang}/{t.slug}",
            "lang": t.lang,
            "title": page["title"],
            "course": t.course,
            "format": t.format,
            "path": out.relative_to(RAW_DIR).as_posix(),
            "url": page["fullurl"],
            "revision_id": page["revisions"][0]["revid"],
            "revision_time": page["revisions"][0]["timestamp"],
            "retrieved": date.today().isoformat(),
            "license": "CC BY-SA 4.0",
        })
        print(f"{t.lang}  {t.format:3}  {page['title']}", flush=True)
        time.sleep(1)

    pd.DataFrame(rows).to_csv(MANIFEST_PATH, index=False)
    print(f"\n{len(rows)} documents -> {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
