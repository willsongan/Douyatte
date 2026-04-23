from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AnalyzeWordRequest, AnalyzeWordResponse, ValidationResult
from app.services.gemini_client import GeminiService, Settings
from app.services.validation import has_only_japanese_chars, normalize_word

app = FastAPI(title="Douyatte API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    return GeminiService(settings=Settings())


@app.post("/api/word/analyze", response_model=AnalyzeWordResponse)
def analyze_word(payload: AnalyzeWordRequest) -> AnalyzeWordResponse:
    word = normalize_word(payload.word)
    if not word:
        raise HTTPException(status_code=400, detail="Word must not be empty.")

    if not has_only_japanese_chars(word):
        return AnalyzeWordResponse(
            validation=ValidationResult(
                is_valid=False,
                reason="Input must contain only Japanese characters (hiragana, katakana, kanji).",
            )
        )

    try:
        validation_result = get_gemini_service().validate_word(word)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Validation model call failed: {exc}") from exc

    if not validation_result.is_valid:
        return AnalyzeWordResponse(validation=validation_result)

    try:
        generated = get_gemini_service().generate_text_sections(word)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Content generation failed: {exc}") from exc

    try:
        audio_result = get_gemini_service().generate_dialogue_audio(word, generated.dialogues)
        audio = audio_result.audio
        directed_prompts = audio_result.directed_prompts
    except Exception:
        audio = []
        directed_prompts = []

    return AnalyzeWordResponse(
        validation=validation_result,
        explanation=generated.explanation,
        dialogues=generated.dialogues,
        audio=audio,
        directed_prompts=directed_prompts,
    )
