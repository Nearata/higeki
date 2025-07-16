from os import environ
from pathlib import Path

from sqlmodel import create_engine


def url() -> str:
    with Path(environ.get("POSTGRES_PASSWORD_FILE", "")) as f:
        PSW = f.read_text().strip()

    return f"postgresql+psycopg://postgres:{PSW}@db/postgres"


engine = create_engine(
    url(), pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=3600
)
