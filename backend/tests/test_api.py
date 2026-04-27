from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db import get_session
from app.main import app
from app.models import CachedWordAnalysis
from app.schemas import (
    AudioSection,
    DialogueScenario,
    DialogueTurn,
    DirectedPromptSection,
    ExplanationSection,
    ValidationResult,
)


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_rejects_non_japanese_input() -> None:
    client = TestClient(app)
    response = client.post("/api/word/analyze", json={"word": "hashi"})
    assert response.status_code == 200
    body = response.json()
    assert body["validation"]["is_valid"] is False
    assert body["directed_prompts"] == []


def test_analyze_uses_cache_for_same_word(monkeypatch) -> None:
    class FakeGeminiService:
        def __init__(self) -> None:
            self.validate_calls = 0
            self.generate_calls = 0
            self.audio_calls = 0

        def validate_word(self, word: str):
            self.validate_calls += 1
            return ValidationResult(is_valid=True, reason="ok")

        def generate_text_sections(self, word: str):
            self.generate_calls += 1
            explanation = ExplanationSection(meaning=f"{word} meaning", usage=f"{word} usage")
            dialogues = [
                DialogueScenario(
                    title="Scenario",
                    context="Context",
                    turns=[DialogueTurn(speaker="A", japanese=word, romaji="romaji", english="english")],
                )
            ]
            return type("Generated", (), {"explanation": explanation, "dialogues": dialogues})()

        def generate_dialogue_audio(self, word: str, dialogues: list):
            self.audio_calls += 1
            return type(
                "AudioResult",
                (),
                {
                    "audio": [AudioSection(scenario_title="Scenario", mime_type="audio/wav", base64_audio="dGVzdA==")],
                    "directed_prompts": [
                        DirectedPromptSection(
                            scenario_title="Scenario",
                            directed_tts_prompt="prompt",
                            style_notes="",
                            used_fallback=False,
                        )
                    ],
                },
            )()

    fake_service = FakeGeminiService()

    monkeypatch.setattr("app.main.get_gemini_service", lambda: fake_service)

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)

    response1 = client.post("/api/word/analyze", json={"word": "食べる"})
    assert response1.status_code == 200
    assert response1.json()["validation"]["is_valid"] is True

    response2 = client.post("/api/word/analyze", json={"word": "食べる"})
    assert response2.status_code == 200
    assert response2.json() == response1.json()

    assert fake_service.validate_calls == 1
    assert fake_service.generate_calls == 1
    assert fake_service.audio_calls == 1

    with Session(engine) as session:
        cached = session.exec(select(CachedWordAnalysis).where(CachedWordAnalysis.word == "食べる")).first()
        assert cached is not None
        assert cached.audio_blob is not None
        assert "base64_audio" not in cached.response_json

    app.dependency_overrides.clear()
