from os import environ
from pathlib import Path

from sqlmodel import create_engine


def url() -> str:
    with Path(environ.get("POSTGRES_PASSWORD_FILE", "")) as f:
        PSW = f.read_text().strip()

    return f"postgresql+psycopg://postgres:{PSW}@db/postgres"


engine = create_engine(url())
