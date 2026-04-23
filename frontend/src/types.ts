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
