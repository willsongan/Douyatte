import type { AudioSection as AudioPayload } from "../types";

type AudioSectionProps = {
  audio?: AudioPayload;
  ttsStatus: string;
};

export function AudioSection({ audio, ttsStatus }: AudioSectionProps) {
  return (
    <section className="card">
      <h3>Conversation Audio</h3>
      {audio ? (
        <audio
          controls
          src={`data:${audio.mime_type};base64,${audio.base64_audio}`}
          className="player"
        />
      ) : (
        <p className="muted">{ttsStatus}</p>
      )}
    </section>
  );
}
