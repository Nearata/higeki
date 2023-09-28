from pydantic import BaseModel


class Item(BaseModel):
    hiding: bool
    # vpn: bool
    # proxy: bool
    # tor: bool
    # relay: bool
    # hosting: bool
