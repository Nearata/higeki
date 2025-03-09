from pydantic import BaseModel


class Item(BaseModel):
    hiding: bool
    flag: str
