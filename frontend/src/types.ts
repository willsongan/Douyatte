export type ValidationResult = {
  is_valid: boolean;
  reason: string;
};

export type ExplanationSection = {
  meaning: string;
  usage: string;
};

export type DialogueTurn = {
  speaker: string;
  japanese: string;
  romaji: string;
  english: string;
};

export type DialogueScenario = {
  title: string;
  context: string;
  turns: DialogueTurn[];
};

export type AudioSection = {
  scenario_title: string;
  mime_type: string;
  base64_audio: string;
};

export type DirectedPromptSection = {
  scenario_title: string;
  directed_tts_prompt: string;
  style_notes: string;
  used_fallback: boolean;
};

export type AnalyzeWordResponse = {
  validation: ValidationResult;
  explanation?: ExplanationSection;
  dialogues: DialogueScenario[];
  audio: AudioSection[];
  directed_prompts: DirectedPromptSection[];
};

export type RegisterVariant = {
  standard: string;
  colloquial: string;
  romaji: string;
  note: string;
};

export type RegisterForms = {
  plain: RegisterVariant;
  polite: RegisterVariant;
  respectful: RegisterVariant;
  humble: RegisterVariant;
};

export type TranslatePhraseResponse = {
  source_phrase: string;
  forms: RegisterForms;
};

export type RegisterKey = keyof RegisterForms;

export const REGISTER_LABELS: Record<RegisterKey, string> = {
  plain: "Plain form",
  polite: "Polite form",
  respectful: "Respectful form",
  humble: "Humble form",
};
