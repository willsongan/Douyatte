from collections.abc import Generator

from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./douyatte_cache.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with engine.begin() as conn:
        inspector = inspect(conn)
        columns = {column["name"] for column in inspector.get_columns("cachedwordanalysis")}
        if "audio_blob" not in columns:
            conn.execute(text("ALTER TABLE cachedwordanalysis ADD COLUMN audio_blob BLOB"))


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
