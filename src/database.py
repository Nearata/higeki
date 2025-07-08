from typing import Optional
from os import environ
from pathlib import Path

from sqlmodel import Field, SQLModel, create_engine
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy import Column


class Network(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cidr: str = Field(sa_column=Column(CIDR, index=True))
    hiding: bool


def url() -> str:
    with Path(environ.get("POSTGRES_PASSWORD_FILE", "")) as f:
        PSW = f.read_text().strip()

    return f"postgresql+psycopg://postgres:{PSW}@db/postgres"

engine = create_engine(url())
