import type { ExplanationSection } from "../types";

type ExplanationCardProps = {
  explanation?: ExplanationSection;
};

export function ExplanationCard({ explanation }: ExplanationCardProps) {
  if (!explanation) {
    return null;
  }

  return (
    <section className="card">
      <h3>How to use this word</h3>
      <p>
        <strong>Meaning:</strong> {explanation.meaning}
      </p>
      <p>
        <strong>Nuance:</strong> {explanation.nuance}
      </p>
      <h4>Usage Notes</h4>
      <ul>
        {explanation.usage_notes.map((note) => (
          <li key={note}>{note}</li>
        ))}
      </ul>
      <h4>Common Patterns</h4>
      <ul>
        {explanation.common_patterns.map((pattern) => (
          <li key={pattern}>{pattern}</li>
        ))}
      </ul>
    </section>
  );
}
