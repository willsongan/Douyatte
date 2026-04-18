type WordFormProps = {
  word: string;
  setWord: (value: string) => void;
  onSubmit: () => void;
  isBusy: boolean;
};

export function WordForm({ word, setWord, onSubmit, isBusy }: WordFormProps) {
  return (
    <section className="card">
      <h2>Enter a Japanese word</h2>
      <p className="muted">Use kana or kanji only. Press Enter to analyze.</p>
      <div className="inputRow">
        <input
          value={word}
          onChange={(e) => setWord(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !isBusy) {
              onSubmit();
            }
          }}
          placeholder="例: 断る"
          autoFocus
        />
        <button onClick={onSubmit} disabled={isBusy || !word.trim()}>
          {isBusy ? "Generating..." : "Analyze"}
        </button>
      </div>
    </section>
  );
}
