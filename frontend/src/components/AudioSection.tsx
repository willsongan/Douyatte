import { useMemo, useState } from "react";
import type { AudioSection as AudioPayload, DirectedPromptSection } from "../types";

type AudioSectionProps = {
  audio: AudioPayload[];
  directedPrompts?: DirectedPromptSection[];
  ttsStatus: string;
};

export function AudioSection({ audio, directedPrompts = [], ttsStatus }: AudioSectionProps) {
  const [showDirectorOutput, setShowDirectorOutput] = useState(false);
  const promptByScenario = useMemo(() => {
    return new Map(directedPrompts.map((item) => [item.scenario_title, item]));
  }, [directedPrompts]);

  return (
    <section className="card">
      <h3>Conversation Audio</h3>
      <button type="button" onClick={() => setShowDirectorOutput((prev) => !prev)}>
        {showDirectorOutput ? "Hide Dev: Director Output" : "Dev: Show Director Output"}
      </button>
      {audio.length ? (
        <>
          {audio.map((clip) => (
            <div key={clip.scenario_title}>
              <p className="muted">{clip.scenario_title}</p>
              <audio
                controls
                src={`data:${clip.mime_type};base64,${clip.base64_audio}`}
                className="player"
              />
              {showDirectorOutput ? (
                <pre style={{ whiteSpace: "pre-wrap", marginTop: "0.75rem" }}>
                  {promptByScenario.get(clip.scenario_title)?.directed_tts_prompt ||
                    "No director output available."}
                </pre>
              ) : null}
            </div>
          ))}
        </>
      ) : (
        <p className="muted">{ttsStatus}</p>
      )}
    </section>
  );
}
