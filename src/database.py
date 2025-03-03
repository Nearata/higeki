from typing import Optional

from sqlmodel import Field, SQLModel, create_engine


class Network(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    address: str = Field(index=True)
    hiding: bool = Field(index=True)


connect_args = {"check_same_thread": False}
engine = create_engine("sqlite:///database.db", echo=False, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
