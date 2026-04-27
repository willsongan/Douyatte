from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class CachedWordAnalysis(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    word: str = Field(index=True, unique=True)
    response_json: str
    audio_blob: bytes | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
