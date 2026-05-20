import base64
import json
import struct
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.db import get_session, init_db
from app.models import CachedWordAnalysis
from app.schemas import (
    AnalyzeWordRequest,
    AnalyzeWordResponse,
    AudioSection,
    TranslatePhraseRequest,
    TranslatePhraseResponse,
    ValidationResult,
)
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


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    return GeminiService(settings=Settings())


def encode_audio_blob(audio_sections: list[AudioSection]) -> bytes | None:
    if not audio_sections:
        return None

    metadata_entries: list[dict[str, int | str]] = []
    chunks: list[bytes] = []
    offset = 0
    for section in audio_sections:
        audio_bytes = base64.b64decode(section.base64_audio)
        length = len(audio_bytes)
        metadata_entries.append(
            {
                "scenario_title": section.scenario_title,
                "mime_type": section.mime_type,
                "offset": offset,
                "length": length,
            }
        )
        chunks.append(audio_bytes)
        offset += length

    metadata = {"version": 1, "entries": metadata_entries}
    metadata_json = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    return struct.pack(">I", len(metadata_json)) + metadata_json + b"".join(chunks)


def decode_audio_blob(audio_blob: bytes | None) -> list[AudioSection]:
    if not audio_blob:
        return []
    if len(audio_blob) < 4:
        return []

    metadata_length = struct.unpack(">I", audio_blob[:4])[0]
    metadata_start = 4
    metadata_end = metadata_start + metadata_length
    if metadata_end > len(audio_blob):
        return []

    metadata = json.loads(audio_blob[metadata_start:metadata_end].decode("utf-8"))
    payload = audio_blob[metadata_end:]
    decoded_audio: list[AudioSection] = []

    for entry in metadata.get("entries", []):
        offset = int(entry["offset"])
        length = int(entry["length"])
        chunk = payload[offset : offset + length]
        if len(chunk) != length:
            return []
        decoded_audio.append(
            AudioSection(
                scenario_title=str(entry["scenario_title"]),
                mime_type=str(entry["mime_type"]),
                base64_audio=base64.b64encode(chunk).decode("ascii"),
            )
        )

    return decoded_audio


@app.post("/api/phrase/translate", response_model=TranslatePhraseResponse)
def translate_phrase(payload: TranslatePhraseRequest) -> TranslatePhraseResponse:
    phrase = payload.phrase.strip()
    if not phrase:
        raise HTTPException(status_code=400, detail="Phrase must not be empty.")

    try:
        return get_gemini_service().translate_phrase_registers(phrase)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Phrase translation failed: {exc}") from exc


@app.post("/api/word/analyze", response_model=AnalyzeWordResponse)
def analyze_word(
    payload: AnalyzeWordRequest,
    session: Session = Depends(get_session),
) -> AnalyzeWordResponse:
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

    cached = session.exec(select(CachedWordAnalysis).where(CachedWordAnalysis.word == word)).first()
    if cached:
        cached_response = AnalyzeWordResponse.model_validate_json(cached.response_json)
        cached_audio = decode_audio_blob(cached.audio_blob)
        if cached_audio:
            return cached_response.model_copy(update={"audio": cached_audio})
        return cached_response

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

    response = AnalyzeWordResponse(
        validation=validation_result,
        explanation=generated.explanation,
        dialogues=generated.dialogues,
        audio=audio,
        directed_prompts=directed_prompts,
    )
    cached = CachedWordAnalysis(
        word=word,
        response_json=response.model_copy(update={"audio": []}).model_dump_json(),
        audio_blob=encode_audio_blob(response.audio),
    )
    session.add(cached)
    session.commit()
    return response
