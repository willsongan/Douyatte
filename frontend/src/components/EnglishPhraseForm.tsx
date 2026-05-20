type EnglishPhraseFormProps = {
  phrase: string;
  setPhrase: (value: string) => void;
  onSubmit: () => void;
  isBusy: boolean;
};

export function EnglishPhraseForm({
  phrase,
  setPhrase,
  onSubmit,
  isBusy,
}: EnglishPhraseFormProps) {
  return (
    <section className="card">
      <h2>Enter an English phrase</h2>
      <p className="muted">
        Get natural Japanese in four speech registers, each with a colloquial variant.
      </p>
      <div className="inputRow">
        <input
          value={phrase}
          onChange={(e) => setPhrase(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !isBusy) {
              onSubmit();
            }
          }}
          placeholder="e.g. I will go tomorrow"
          autoFocus
        />
        <button onClick={onSubmit} disabled={isBusy || !phrase.trim()}>
          {isBusy ? "Translating..." : "Translate"}
        </button>
      </div>
    </section>
  );
}
