from course_rag.ingest import clean_wiki_math, split_sections


def test_formula_residue_is_replaced_by_inline_latex():
    raw = "Si \n  \n    \n      n\n    \n    {\\displaystyle n}\n  \n tâches doivent être exécutées.\n"
    assert clean_wiki_math(raw).strip() == "Si n tâches doivent être exécutées."


def test_short_real_lines_are_kept():
    raw = "Les méthodes HTTP :\nGET\nPOST\nDELETE\n"
    assert clean_wiki_math(raw) == raw


def test_sections_nest_and_reference_sections_are_dropped():
    text = (
        "# Title\nIntro text.\n\n## Algorithm\n### Bagging\nBagging text.\n\n"
        "## Références\n1. Some book\n\n## Bibliographie\n### En anglais\nAnother book\n"
    )
    sections = split_sections(text, "Title")
    assert [s.path for s in sections] == ["", "Algorithm > Bagging"]
    assert sections[1].body == "Bagging text."


def test_arabic_reference_heading_is_dropped():
    sections = split_sections("# عنوان\nنص.\n\n## المراجع\nكتاب\n\n## انظر أيضاً\nرابط\n", "عنوان")
    assert [s.body for s in sections] == ["نص."]
