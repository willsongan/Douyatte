import type { DialogueScenario } from "../types";

type DialogueCardProps = {
  dialogues: DialogueScenario[];
  showRomaji: boolean;
  setShowRomaji: (value: boolean) => void;
  showEnglish: boolean;
  setShowEnglish: (value: boolean) => void;
};

export function DialogueCard({
  dialogues,
  showRomaji,
  setShowRomaji,
  showEnglish,
  setShowEnglish,
}: DialogueCardProps) {
  if (!dialogues.length) {
    return null;
  }

  return (
    <section className="card">
      <div className="rowBetween">
        <h3>Realistic Dialogues</h3>
        <div className="toggles">
          <label>
            <input
              type="checkbox"
              checked={showRomaji}
              onChange={(e) => setShowRomaji(e.target.checked)}
            />
            Romaji
          </label>
          <label>
            <input
              type="checkbox"
              checked={showEnglish}
              onChange={(e) => setShowEnglish(e.target.checked)}
            />
            English
          </label>
        </div>
      </div>

      {dialogues.map((scenario) => (
        <article key={scenario.title} className="scenario">
          <h4>{scenario.title}</h4>
          <p className="muted">{scenario.context}</p>
          <div className="dialogueList">
            {scenario.turns.map((turn, idx) => (
              <div key={`${scenario.title}-${idx}`} className="turn">
                <p>
                  <strong>{turn.speaker}:</strong> {turn.japanese}
                </p>
                {showRomaji ? <p className="muted">{turn.romaji}</p> : null}
                {showEnglish ? <p>{turn.english}</p> : null}
              </div>
            ))}
          </div>
        </article>
      ))}
    </section>
  );
}
