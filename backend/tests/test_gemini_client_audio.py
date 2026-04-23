import io
import wave

from app.schemas import DialogueScenario, DialogueTurn
from app.services.gemini_client import GeminiService


def test_normalize_audio_for_browser_wraps_pcm_into_wav() -> None:
    pcm_silence = b"\x00\x00" * 240  # 10ms at 24kHz mono, 16-bit
    mime_type, wav_bytes = GeminiService._normalize_audio_for_browser("audio/L16;rate=24000", pcm_silence)

    assert mime_type == "audio/wav"
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getframerate() == 24000
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.readframes(240) == pcm_silence


def _sample_scenario() -> DialogueScenario:
    return DialogueScenario(
        title="Scenario A",
        context="Quick context",
        turns=[
            DialogueTurn(speaker="A", japanese="知人から聞いた。", romaji="", english="I heard it from an acquaintance."),
            DialogueTurn(speaker="B", japanese="なるほど。", romaji="", english="I see."),
        ],
    )


def test_generate_dialogue_audio_uses_director_prompt_when_available() -> None:
    service = GeminiService.__new__(GeminiService)

    def fake_basic(_: GeminiService, scenario: DialogueScenario) -> str:
        return f"BASIC::{scenario.title}"

    def fake_directed(_: GeminiService, *, word: str, scenario: DialogueScenario) -> tuple[str, str]:
        return f"DIRECTED::{word}::{scenario.title}", "Natural and conversational."

    def fake_audio(_: GeminiService, tts_text: str) -> tuple[str, str]:
        return "audio/wav", f"encoded::{tts_text}"

    service._build_basic_tts_text = fake_basic.__get__(service, GeminiService)  # type: ignore[attr-defined]
    service._generate_directed_tts_prompt = fake_directed.__get__(service, GeminiService)  # type: ignore[attr-defined]
    service._generate_audio_base64_from_tts_text = fake_audio.__get__(service, GeminiService)  # type: ignore[attr-defined]

    result = service.generate_dialogue_audio("知人", [_sample_scenario()])

    assert len(result.audio) == 1
    assert result.audio[0].base64_audio == "encoded::DIRECTED::知人::Scenario A"
    assert len(result.directed_prompts) == 1
    assert result.directed_prompts[0].used_fallback is False
    assert result.directed_prompts[0].style_notes == "Natural and conversational."


def test_generate_dialogue_audio_falls_back_when_director_fails() -> None:
    service = GeminiService.__new__(GeminiService)

    def fake_basic(_: GeminiService, scenario: DialogueScenario) -> str:
        return f"BASIC::{scenario.title}"

    def fake_directed(_: GeminiService, *, word: str, scenario: DialogueScenario) -> tuple[str, str]:
        raise ValueError("director failed")

    def fake_audio(_: GeminiService, tts_text: str) -> tuple[str, str]:
        return "audio/wav", f"encoded::{tts_text}"

    service._build_basic_tts_text = fake_basic.__get__(service, GeminiService)  # type: ignore[attr-defined]
    service._generate_directed_tts_prompt = fake_directed.__get__(service, GeminiService)  # type: ignore[attr-defined]
    service._generate_audio_base64_from_tts_text = fake_audio.__get__(service, GeminiService)  # type: ignore[attr-defined]

    result = service.generate_dialogue_audio("知人", [_sample_scenario()])

    assert len(result.audio) == 1
    assert result.audio[0].base64_audio == "encoded::BASIC::Scenario A"
    assert len(result.directed_prompts) == 1
    assert result.directed_prompts[0].used_fallback is True
