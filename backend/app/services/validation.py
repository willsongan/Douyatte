import re


_JAPANESE_CHAR_PATTERN = re.compile(r"^[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\u3005\u30fc]+$")


def normalize_word(value: str) -> str:
    return value.strip()


def has_only_japanese_chars(value: str) -> bool:
    return bool(_JAPANESE_CHAR_PATTERN.fullmatch(value))
