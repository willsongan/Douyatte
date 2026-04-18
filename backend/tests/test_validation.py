from app.services.validation import has_only_japanese_chars, normalize_word


def test_normalize_word_strips_spaces() -> None:
    assert normalize_word("  断る  ") == "断る"


def test_has_only_japanese_chars() -> None:
    assert has_only_japanese_chars("断る")
    assert has_only_japanese_chars("カタカナ")
    assert not has_only_japanese_chars("kotowaru")
    assert not has_only_japanese_chars("断る1")
