from typing import Optional

from sqlmodel import Field, SQLModel, create_engine


class Network(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cidr: str = Field(index=True)
    network: int = Field()
    broadcast: int = Field()
    hiding: bool = Field()
    flag: Optional[str] = Field()


engine = create_engine(
    "sqlite:///data/sqlite.db", echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
