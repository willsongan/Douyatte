import { useState } from "react";
import { EnglishPhraseForm } from "../components/EnglishPhraseForm";
import { RegisterFormsCard } from "../components/RegisterFormsCard";
import type { TranslatePhraseResponse } from "../types";

const API_BASE = "http://127.0.0.1:8000";

type NewFeatureIterationProps = {
  onBack: () => void;
};

export function NewFeatureIteration({ onBack }: NewFeatureIterationProps) {
  const [phrase, setPhrase] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<TranslatePhraseResponse | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [showRomaji, setShowRomaji] = useState(false);
  const [phase, setPhase] = useState("Idle");

  async function onSubmit() {
    if (!phrase.trim()) {
      setError("Please enter an English phrase.");
      return;
    }

    setError("");
    setResult(null);
    setIsBusy(true);
    setShowRomaji(false);
    setPhase("Translating across speech registers...");

    try {
      const response = await fetch(`${API_BASE}/api/phrase/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phrase }),
      });

      if (!response.ok) {
        const body = await response.text();
        throw new Error(body || "Request failed.");
      }

      const data = (await response.json()) as TranslatePhraseResponse;
      setResult(data);
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
      <header className="iterationHeader">
        <button type="button" className="backButton" onClick={onBack}>
          Back
        </button>
        <div>
          <h1>Phrase registers</h1>
          <p className="muted">
            Translate an English phrase into plain, polite, respectful, and humble Japanese.
          </p>
        </div>
      </header>

      <EnglishPhraseForm
        phrase={phrase}
        setPhrase={setPhrase}
        onSubmit={onSubmit}
        isBusy={isBusy}
      />

      <p className="status">{phase}</p>
      {error ? <p className="error">{error}</p> : null}

      {result ? (
        <RegisterFormsCard
          sourcePhrase={result.source_phrase}
          forms={result.forms}
          showRomaji={showRomaji}
          setShowRomaji={setShowRomaji}
        />
      ) : null}
    </main>
  );
}
