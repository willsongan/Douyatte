import base64
import json
from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import types
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas import DialogueScenario, ExplanationSection, ValidationResult
from app.services.prompts import dialogues_prompt, explanation_prompt, validation_prompt


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_validation_model: str = "gemini-3-flash-lite"
    gemini_generation_model: str = "gemini-3-flash-preview"
    gemini_tts_model: str = "gemini-3.1-flash-tts-preview"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@dataclass
class GeneratedText:
    explanation: ExplanationSection
    dialogues: list[DialogueScenario]


class GeminiService:
    def __init__(self, settings: Settings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._validation_model = settings.gemini_validation_model
        self._generation_model = settings.gemini_generation_model
        self._tts_model = settings.gemini_tts_model

    def _generate_json(self, *, model: str, prompt: str) -> Any:
        response = self._client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json"),
        )
        if not response.text:
            raise ValueError("Gemini returned empty response text.")
        return json.loads(response.text)

    def validate_word(self, word: str) -> ValidationResult:
        payload = self._generate_json(model=self._validation_model, prompt=validation_prompt(word))
        return ValidationResult.model_validate(payload)

    def generate_text_sections(self, word: str) -> GeneratedText:
        explanation_payload = self._generate_json(model=self._generation_model, prompt=explanation_prompt(word))
        dialogues_payload = self._generate_json(model=self._generation_model, prompt=dialogues_prompt(word))

        explanation = ExplanationSection.model_validate(explanation_payload)
        dialogues = [DialogueScenario.model_validate(item) for item in dialogues_payload.get("dialogues", [])]
        return GeneratedText(explanation=explanation, dialogues=dialogues)

    def generate_dialogue_audio_base64(self, dialogues: list[DialogueScenario]) -> tuple[str, str]:
        lines: list[str] = []
        speaker_voice_map: dict[str, str] = {}
        available_voices = ["Kore", "Leda", "Aoede", "Callirrhoe", "Puck", "Fenrir"]

        for scenario in dialogues:
            for turn in scenario.turns:
                if turn.speaker not in speaker_voice_map:
                    speaker_voice_map[turn.speaker] = available_voices[len(speaker_voice_map) % len(available_voices)]
                voice = speaker_voice_map[turn.speaker]
                lines.append(f"[{turn.speaker}|{voice}] {turn.japanese}")

        if not lines:
            raise ValueError("No dialogue lines available for TTS.")

        tts_text = "会話です。 " + " ".join(lines)
        response = self._client.models.generate_content(
            model=self._tts_model,
            contents=tts_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                    )
                ),
            ),
        )

        for candidate in response.candidates or []:
            for part in candidate.content.parts or []:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and inline_data.data:
                    return inline_data.mime_type or "audio/wav", base64.b64encode(inline_data.data).decode("utf-8")

        raise ValueError("No audio data returned from TTS generation.")
