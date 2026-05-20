from typing import List, Optional

from pydantic import BaseModel, Field


class AnalyzeWordRequest(BaseModel):
    word: str = Field(min_length=1, max_length=30)


class ValidationResult(BaseModel):
    is_valid: bool
    reason: str


class ExplanationSection(BaseModel):
    meaning: str
    usage: str


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
    scenario_title: str
    mime_type: str
    base64_audio: str


class DirectedPromptSection(BaseModel):
    scenario_title: str
    directed_tts_prompt: str
    style_notes: str = ""
    used_fallback: bool = False


class AnalyzeWordResponse(BaseModel):
    validation: ValidationResult
    explanation: Optional[ExplanationSection] = None
    dialogues: List[DialogueScenario] = Field(default_factory=list)
    audio: List[AudioSection] = Field(default_factory=list)
    directed_prompts: List[DirectedPromptSection] = Field(default_factory=list)


class TranslatePhraseRequest(BaseModel):
    phrase: str = Field(min_length=1, max_length=200)


class RegisterVariant(BaseModel):
    standard: str
    colloquial: str
    romaji: str = ""
    note: str = ""


class RegisterForms(BaseModel):
    plain: RegisterVariant
    polite: RegisterVariant
    respectful: RegisterVariant
    humble: RegisterVariant


class TranslatePhraseResponse(BaseModel):
    source_phrase: str
    forms: RegisterForms
