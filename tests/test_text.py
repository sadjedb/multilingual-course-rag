from course_rag.text import bm25_tokenize, detect_language, normalize_arabic, normalize_for_match, split_sentences


def test_arabic_spelling_variants_fold_together():
    # with/without short vowels, hamza on the alef, ta marbuta vs ha
    assert normalize_arabic("تَعَلُّم الآلَة") == normalize_arabic("تعلم الالة")
    assert normalize_arabic("أحمد") == normalize_arabic("احمد")
    assert normalize_arabic("مدرسة") == normalize_arabic("مدرسه")


def test_bm25_tokens_drop_article_and_stopwords():
    assert bm25_tokenize("والشبكة في الحاسوب") == ["شبكه", "حاسوب"]
    assert bm25_tokenize("Qu'est-ce que la mémoire virtuelle ?") == ["memoire", "virtuelle"]
    assert bm25_tokenize("What is the transformer?") == ["transformer"]


def test_detect_language():
    assert detect_language("ما هو نظام أسماء النطاقات؟") == "ar"
    assert detect_language("Qu'est-ce qu'un interblocage ?") == "fr"
    assert detect_language("Comment fonctionne la descente de gradient ?") == "fr"
    assert detect_language("How does k-fold cross-validation work?") == "en"
    assert detect_language("ما هو بروتوكول HTTP و TCP؟") == "ar"  # Latin acronyms inside Arabic


def test_match_normalisation_ignores_punctuation_and_citation_marks():
    assert normalize_for_match("L'index « B-tree »[3], est rapide.") == normalize_for_match("l index b tree est rapide")


def test_split_sentences_handles_arabic_question_mark():
    assert split_sentences("ما هو؟ هذا مثال. Second one!") == ["ما هو؟", "هذا مثال.", "Second one!"]
