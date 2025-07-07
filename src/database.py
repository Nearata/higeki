from typing import Optional
from os import environ
from pathlib import Path

from sqlmodel import Field, SQLModel, create_engine


class Network(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cidr: str = Field(index=True)
    network: int
    broadcast: int
    hiding: bool


with Path(environ.get("POSTGRES_PASSWORD_FILE", "")) as f:
    PSW = f.read_text().strip()

engine = create_engine(f"postgresql+psycopg://postgres:{PSW}@db/postgres")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
