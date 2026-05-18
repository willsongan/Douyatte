type NewFeatureIterationProps = {
  onBack: () => void;
};

export function NewFeatureIteration({ onBack }: NewFeatureIterationProps) {
  return (
    <main className="container">
      <header className="iterationHeader">
        <button type="button" className="backButton" onClick={onBack}>
          Back
        </button>
        <div>
          <h1>New feature</h1>
          <p className="muted">Placeholder for the next prototype iteration.</p>
        </div>
      </header>

      <section className="card">
        <p>Build your next experiment here without touching the word-context flow.</p>
      </section>
    </main>
  );
}
