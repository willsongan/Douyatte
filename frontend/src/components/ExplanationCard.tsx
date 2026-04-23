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
        <strong>Usage:</strong> {explanation.usage}
      </p>
    </section>
  );
}
