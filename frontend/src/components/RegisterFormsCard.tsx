import { REGISTER_LABELS, type RegisterForms, type RegisterKey } from "../types";

type RegisterFormsCardProps = {
  sourcePhrase: string;
  forms: RegisterForms;
  showRomaji: boolean;
  setShowRomaji: (value: boolean) => void;
};

const REGISTER_ORDER: RegisterKey[] = ["plain", "polite", "respectful", "humble"];

export function RegisterFormsCard({
  sourcePhrase,
  forms,
  showRomaji,
  setShowRomaji,
}: RegisterFormsCardProps) {
  return (
    <section className="card">
      <div className="rowBetween">
        <div>
          <h3>Japanese registers</h3>
          <p className="muted">Source: {sourcePhrase}</p>
        </div>
        <div className="toggles">
          <label>
            <input
              type="checkbox"
              checked={showRomaji}
              onChange={(e) => setShowRomaji(e.target.checked)}
            />
            Romaji
          </label>
        </div>
      </div>

      {REGISTER_ORDER.map((register) => {
        const variant = forms[register];
        return (
          <article key={register} className="registerBlock">
            <h4>{REGISTER_LABELS[register]}</h4>
            <p>
              <strong>Standard:</strong> {variant.standard}
            </p>
            {showRomaji && variant.romaji ? (
              <p className="muted">{variant.romaji}</p>
            ) : null}
            <p>
              <strong>Colloquial:</strong> {variant.colloquial}
            </p>
            {variant.note ? <p className="muted">{variant.note}</p> : null}
          </article>
        );
      })}
    </section>
  );
}
