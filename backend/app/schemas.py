from typing import List, Optional

from pydantic import BaseModel, Field


class AnalyzeWordRequest(BaseModel):
    word: str = Field(min_length=1, max_length=30)


class ValidationResult(BaseModel):
    is_valid: bool
    reason: str


class ExplanationSection(BaseModel):
    meaning: str
    nuance: str
    usage_notes: List[str]
    common_patterns: List[str]


class DialogueTurn(BaseModel):
    speaker: str
    japanese: str
    romaji: str
    english: str


class DialogueScenario(BaseModel):
    title: str
    context: str
    turns: List[DialogueTurn]


class AudioSection(BaseModel):
    mime_type: str
    base64_audio: str


class AnalyzeWordResponse(BaseModel):
    validation: ValidationResult
    explanation: Optional[ExplanationSection] = None
    dialogues: List[DialogueScenario] = Field(default_factory=list)
    audio: Optional[AudioSection] = None
