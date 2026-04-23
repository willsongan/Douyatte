import { useMemo, useState } from "react";
import { AudioSection } from "./components/AudioSection";
import { DialogueCard } from "./components/DialogueCard";
import { ExplanationCard } from "./components/ExplanationCard";
import { WordForm } from "./components/WordForm";
import type { AnalyzeWordResponse } from "./types";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [word, setWord] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalyzeWordResponse | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [showRomaji, setShowRomaji] = useState(false);
  const [showEnglish, setShowEnglish] = useState(false);
  const [phase, setPhase] = useState("Idle");

  const ttsStatus = useMemo(() => {
    if (result?.audio.length) return "Audio ready.";
    if (isBusy) return "Generating audio...";
    return "No audio generated yet.";
  }, [isBusy, result?.audio]);

  async function onSubmit() {
    if (!word.trim()) {
      setError("Please enter a Japanese word.");
      return;
    }

    setError("");
    setResult(null);
    setIsBusy(true);
    setShowRomaji(false);
    setShowEnglish(false);
    setPhase("Validating input...");

    try {
      setPhase("Generating explanation, dialogues, and audio...");
      const response = await fetch(`${API_BASE}/api/word/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word }),
      });

      if (!response.ok) {
        const body = await response.text();
        throw new Error(body || "Request failed.");
      }

      const data = (await response.json()) as AnalyzeWordResponse;
      setResult(data);
      if (!data.validation.is_valid) {
        setError(data.validation.reason);
      }
      setPhase("Done");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unexpected error.";
      setError(message);
      setPhase("Failed");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="container">
      <header>
        <h1>Douyatte</h1>
        <p className="muted">
          Learn how Japanese words are used in realistic context.
        </p>
      </header>

      <WordForm word={word} setWord={setWord} onSubmit={onSubmit} isBusy={isBusy} />

      <p className="status">{phase}</p>
      {error ? <p className="error">{error}</p> : null}

      {result?.validation.is_valid ? (
        <>
          <ExplanationCard explanation={result.explanation} />
          <DialogueCard
            dialogues={result.dialogues}
            showRomaji={showRomaji}
            setShowRomaji={setShowRomaji}
            showEnglish={showEnglish}
            setShowEnglish={setShowEnglish}
          />
          <AudioSection
            audio={result.audio}
            directedPrompts={result.directed_prompts}
            ttsStatus={ttsStatus}
          />
        </>
      ) : null}
    </main>
  );
}

export default App;
