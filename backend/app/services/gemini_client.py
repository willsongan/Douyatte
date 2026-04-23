import base64
import io
import json
import re
import wave
from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import types
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas import (
    AudioSection,
    DialogueScenario,
    DirectedPromptSection,
    ExplanationSection,
    ValidationResult,
)
from app.services.prompts import director_prompt, dialogues_prompt, explanation_prompt, validation_prompt


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_validation_model: str = "gemini-2.5-flash-lite"
    gemini_generation_model: str = "gemini-3-flash-preview"
    gemini_tts_model: str = "gemini-3.1-flash-tts-preview"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@dataclass
class GeneratedText:
    explanation: ExplanationSection
    dialogues: list[DialogueScenario]


@dataclass
class AudioGenerationResult:
    audio: list[AudioSection]
    directed_prompts: list[DirectedPromptSection]


class GeminiService:
    # Manual voice mapping entry points:
    # Add or reorder voice names in these lists to control male/female speaker voice selection.
    FEMALE_VOICE_CONFIGS = ["Kore", "Leda", "Aoede", "Callirrhoe"]
    MALE_VOICE_CONFIGS = ["Puck", "Fenrir"]
    FALLBACK_VOICE_CONFIGS = ["Kore", "Leda", "Aoede", "Callirrhoe", "Puck", "Fenrir"]

    def __init__(self, settings: Settings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._validation_model = settings.gemini_validation_model
        self._generation_model = settings.gemini_generation_model
        self._tts_model = settings.gemini_tts_model

    @staticmethod
    def _pcm_to_wav(raw_pcm: bytes, *, sample_rate: int, channels: int = 1, sample_width: int = 2) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(raw_pcm)
        return buffer.getvalue()

    @staticmethod
    def _normalize_audio_for_browser(mime_type: str | None, data: bytes) -> tuple[str, bytes]:
        normalized_mime = (mime_type or "").strip()
        if not normalized_mime:
            return "audio/wav", data

        lower_mime = normalized_mime.lower()
        if lower_mime.startswith("audio/l16") or lower_mime.startswith("audio/pcm"):
            sample_rate_match = re.search(r"rate=(\d+)", lower_mime)
            sample_rate = int(sample_rate_match.group(1)) if sample_rate_match else 24000
            wav_data = GeminiService._pcm_to_wav(data, sample_rate=sample_rate)
            return "audio/wav", wav_data

        return normalized_mime, data

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
        explanation = ExplanationSection.model_validate(explanation_payload)
        dialogues_payload = self._generate_json(
            model=self._generation_model, prompt=dialogues_prompt(word, explanation.usage)
        )
        dialogues = [DialogueScenario.model_validate(item) for item in dialogues_payload.get("dialogues", [])]
        return GeneratedText(explanation=explanation, dialogues=dialogues)

    def _generate_scenario_audio_base64(self, scenario: DialogueScenario) -> tuple[str, str]:
        return self._generate_audio_base64_from_turns(scenario)

    def _build_basic_tts_text(self, scenario: DialogueScenario) -> str:
        lines = [f"{turn.speaker}: {turn.japanese}" for turn in scenario.turns]

        if not lines:
            raise ValueError("No dialogue lines available for TTS.")

        return "会話です。 " + " ".join(lines)

    @staticmethod
    def _extract_gender_label(speaker: str) -> str | None:
        match = re.search(r"(female|male)\s*\d+", speaker, flags=re.IGNORECASE)
        if not match:
            return None
        return match.group(1).lower()

    @staticmethod
    def _strip_gender_tag_from_speaker(speaker: str) -> str:
        cleaned = re.sub(r"[\(\[\{]?\s*(female|male)\s*\d+\s*[\)\]\}]?", "", speaker, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        cleaned = cleaned.strip(" -:|")
        return cleaned or speaker.strip()

    def _strip_gender_tags_from_dialogues(self, dialogues: list[DialogueScenario]) -> None:
        for scenario in dialogues:
            for turn in scenario.turns:
                turn.speaker = self._strip_gender_tag_from_speaker(turn.speaker)

    def _pick_unique_voice(self, pool: list[str], used: set[str]) -> str:
        for voice in pool:
            if voice not in used:
                return voice
        raise ValueError("Not enough unique voice configs for speakers in this scenario.")

    def _build_speaker_voice_map(self, scenario: DialogueScenario) -> dict[str, str]:
        voice_map: dict[str, str] = {}
        used_voices: set[str] = set()

        for turn in scenario.turns:
            speaker = turn.speaker
            if speaker in voice_map:
                continue
            gender = self._extract_gender_label(speaker)
            if gender == "female":
                voice = self._pick_unique_voice(self.FEMALE_VOICE_CONFIGS, used_voices)
            elif gender == "male":
                voice = self._pick_unique_voice(self.MALE_VOICE_CONFIGS, used_voices)
            else:
                voice = self._pick_unique_voice(self.FALLBACK_VOICE_CONFIGS, used_voices)
            voice_map[speaker] = voice
            used_voices.add(voice)
        return voice_map

    def _generate_directed_tts_prompt(self, *, word: str, scenario: DialogueScenario) -> tuple[str, str]:
        transcript = "\n".join(f"{turn.speaker}: {turn.japanese}" for turn in scenario.turns)
        payload = self._generate_json(
            model=self._generation_model,
            prompt=director_prompt(word, scenario.title, scenario.context, transcript),
        )
        directed_tts_prompt = str(payload.get("directed_tts_prompt", "")).strip()
        style_notes = str(payload.get("style_notes", "")).strip()
        if not directed_tts_prompt:
            raise ValueError("Director returned empty directed_tts_prompt.")
        return directed_tts_prompt, style_notes

    def _generate_audio_bytes_from_tts_text(self, tts_text: str, *, voice_name: str) -> tuple[str, bytes]:
        response = self._client.models.generate_content(
            model=self._tts_model,
            contents=tts_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                    )
                ),
            ),
        )

        for candidate in response.candidates or []:
            for part in candidate.content.parts or []:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and inline_data.data:
                    browser_mime, browser_data = self._normalize_audio_for_browser(
                        inline_data.mime_type, inline_data.data
                    )
                    return browser_mime, browser_data

        raise ValueError("No audio data returned from TTS generation.")

    @staticmethod
    def _combine_wav_segments(segments: list[bytes]) -> bytes:
        if not segments:
            raise ValueError("No audio segments to combine.")

        output = io.BytesIO()
        with wave.open(io.BytesIO(segments[0]), "rb") as first_wav:
            channels = first_wav.getnchannels()
            sample_width = first_wav.getsampwidth()
            sample_rate = first_wav.getframerate()
            all_frames = [first_wav.readframes(first_wav.getnframes())]

        silence_frames = b"\x00" * (sample_width * channels * int(sample_rate * 0.12))
        for segment in segments[1:]:
            with wave.open(io.BytesIO(segment), "rb") as wav_file:
                if (
                    wav_file.getnchannels() != channels
                    or wav_file.getsampwidth() != sample_width
                    or wav_file.getframerate() != sample_rate
                ):
                    raise ValueError("Mismatched WAV parameters while combining dialogue audio.")
                all_frames.append(silence_frames)
                all_frames.append(wav_file.readframes(wav_file.getnframes()))

        with wave.open(output, "wb") as out_wav:
            out_wav.setnchannels(channels)
            out_wav.setsampwidth(sample_width)
            out_wav.setframerate(sample_rate)
            out_wav.writeframes(b"".join(all_frames))
        return output.getvalue()

    def _generate_audio_base64_from_turns(self, scenario: DialogueScenario) -> tuple[str, str]:
        if not scenario.turns:
            raise ValueError("No dialogue lines available for TTS.")

        speaker_voice_map = self._build_speaker_voice_map(scenario)
        wav_segments: list[bytes] = []
        for turn in scenario.turns:
            voice_name = speaker_voice_map[turn.speaker]
            mime_type, audio_bytes = self._generate_audio_bytes_from_tts_text(turn.japanese, voice_name=voice_name)
            if mime_type.lower() != "audio/wav":
                raise ValueError(f"Expected audio/wav from TTS, got {mime_type}")
            wav_segments.append(audio_bytes)

        combined_wav = self._combine_wav_segments(wav_segments)
        return "audio/wav", base64.b64encode(combined_wav).decode("utf-8")

    def generate_dialogue_audio(self, word: str, dialogues: list[DialogueScenario]) -> AudioGenerationResult:
        scenario_audio: list[AudioSection] = []
        directed_prompts: list[DirectedPromptSection] = []
        for scenario in dialogues:
            fallback_text = self._build_basic_tts_text(scenario)
            tts_text = fallback_text
            style_notes = ""
            used_fallback = True
            try:
                tts_text, style_notes = self._generate_directed_tts_prompt(word=word, scenario=scenario)
                used_fallback = False
            except Exception:
                # Use plain transcript-style prompting if director step fails.
                tts_text = fallback_text

            mime_type, base64_audio = self._generate_audio_base64_from_turns(scenario)
            scenario_audio.append(
                AudioSection(scenario_title=scenario.title, mime_type=mime_type, base64_audio=base64_audio)
            )
            directed_prompts.append(
                DirectedPromptSection(
                    scenario_title=scenario.title,
                    directed_tts_prompt=tts_text,
                    style_notes=style_notes,
                    used_fallback=used_fallback,
                )
            )
        # Hide maleN/femaleN tokens from frontend after internal voice assignment is done.
        self._strip_gender_tags_from_dialogues(dialogues)
        return AudioGenerationResult(audio=scenario_audio, directed_prompts=directed_prompts)
