export type ValidationResult = {
  is_valid: boolean;
  reason: string;
};

export type ExplanationSection = {
  meaning: string;
  nuance: string;
  usage_notes: string[];
  common_patterns: string[];
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
  mime_type: string;
  base64_audio: string;
};

export type AnalyzeWordResponse = {
  validation: ValidationResult;
  explanation?: ExplanationSection;
  dialogues: DialogueScenario[];
  audio?: AudioSection;
};
