def validation_prompt(word: str) -> str:
    return (
        "Evaluate this Japanese input and return JSON only.\n"
        'Schema: {"is_valid": boolean, "reason": string}\n'
        "Criteria for True:\n"
        "1. Must use ONLY Japanese characters (Hiragana, Katakana, or Kanji). No Romaji/Latin.\n"
        "2. If there are multiple characters, all together they must form one lexical word.\n"
        "3. Must not be ambiguous Hiragana-only inputs like はし or かける when kanji would be needed to be specific.\n"
        f"Input: {word}\n"
        "Return only the JSON object."
    )


def explanation_prompt(word: str) -> str:
    return (
        "You are helping learners understand HOW to use a Japanese word in real life.\n"
        "Return JSON only.\n"
        'Schema: {"meaning": string, "nuance": string, "usage_notes": string[], "common_patterns": string[]}\n'
        "Keep explanations practical, concise, and learner-friendly.\n"
        f"Word: {word}"
    )


def dialogues_prompt(word: str) -> str:
    return (
        "Create realistic, colloquial scenarios and dialogues using this Japanese word naturally.\n"
        "Return JSON only.\n"
        'Schema: {"dialogues": [{"title": string, "context": string, "turns": [{"speaker": string, "japanese": string, "romaji": string, "english": string}]}]}\n'
        "Generate 2 scenarios, each with 6-8 turns.\n"
        "Japanese lines must sound natural in modern daily conversation.\n"
        f"Word: {word}"
    )
