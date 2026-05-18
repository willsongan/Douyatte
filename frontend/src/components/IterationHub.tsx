type IterationHubProps = {
  onSelectIteration1: () => void;
  onSelectIteration2: () => void;
};

export function IterationHub({
  onSelectIteration1,
  onSelectIteration2,
}: IterationHubProps) {
  return (
    <main className="container hub">
      <header>
        <h1>Douyatte</h1>
        <p className="muted">Prototype hub — pick an iteration to open.</p>
      </header>

      <nav className="iterationList" aria-label="Prototype iterations">
        <button type="button" className="iterationButton" onClick={onSelectIteration1}>
          <span className="iterationButtonTitle">Iteration 1 — Word context</span>
          <span className="iterationButtonDesc">
            Analyze a word, read explanations, dialogues, and audio.
          </span>
        </button>

        <button type="button" className="iterationButton" onClick={onSelectIteration2}>
          <span className="iterationButtonTitle">Iteration 2 — New feature</span>
          <span className="iterationButtonDesc">
            Empty shell for the next experiment.
          </span>
        </button>
      </nav>
    </main>
  );
}
