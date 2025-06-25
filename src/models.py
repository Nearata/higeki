from typing import Optional

from pydantic import BaseModel


class Item(BaseModel):
    hiding: bool
    flag: Optional[str]
