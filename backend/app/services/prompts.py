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
        "You are helping learners understand how to use a Japanese word in real life.\n"
        "Return JSON only.\n"
        'Return exactly this shape: {"meaning": string, "usage": string}\n'
        "Keep it concise and practical.\n"
        "meaning: short plain-English definition.\n"
        "usage: 1-2 learner-friendly sentences combining nuance and usage notes.\n"
        f"Word: {word}"
    )


def dialogues_prompt(word: str, usage_context: str) -> str:
    return (
        "Create short, practical Japanese dialogues that clearly teach when to use this word.\n"
        "Return JSON only.\n"
        'Return exactly this shape: {"dialogues": [{"title": string, "context": string, "turns": [{"speaker": string, "japanese": string, "romaji": string, "english": string}]}]}\n'
        "Generate exactly 2 scenarios with clearly different use-cases.\n"
        "Each scenario context must explain the situation in plain English (when this word is used).\n"
        "Keep each scenario very short: target 2 turns total, minimum 2 turns, maximum 4 turns.\n"
        "Use two speakers in every scenario.\n"
        "In each scenario, include a gender id in each speaker field as maleN or femaleN (e.g., Yui female1, Emi female2, Ken male1).\n"
        "If both speakers are women, use female1 and female2. If both are men, use male1 and male2.\n"
        "Keep the speaker labels human-readable names plus the gender id token.\n"
        "Keep Japanese lines natural in modern daily conversation.\n"
        "Make both scenarios easy for beginners to distinguish.\n"
        f"Usage context: {usage_context}\n"
        f"Word: {word}"
    )


def director_prompt(word: str, scenario_title: str, scenario_context: str, transcript: str) -> str:
    return (
        "You are a voice director preparing an advanced prompt for Gemini TTS.\n"
        "Return JSON only.\n"
        'Return exactly this shape: {"directed_tts_prompt": string, "style_notes": string}\n'
        "Goal: keep the same meaning and speaker intent, but make delivery sound naturally human and expressive.\n"
        "Build the directed_tts_prompt with these sections and labels exactly:\n"
        "# AUDIO PROFILE\n"
        "## THE SCENE\n"
        "### DIRECTOR'S NOTES\n"
        "### TRANSCRIPT\n"
        "Rules:\n"
        "- Keep transcript content faithful to the source dialogue meaning.\n"
        "- Keep wording concise; do not add long narration.\n"
        "- Use light, selective audio tags in English only (for example [curious], [slight pause], [warmly]).\n"
        "- Avoid over-tagging and avoid robotic or theatrical overacting.\n"
        "- Do not include markdown code fences.\n"
        "- The TRANSCRIPT section must include speaker-prefixed lines suitable for TTS.\n"
        f"Word: {word}\n"
        f"Scenario title: {scenario_title}\n"
        f"Scenario context: {scenario_context}\n"
        f"Source transcript:\n{transcript}"
    )
