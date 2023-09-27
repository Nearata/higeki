from contextlib import asynccontextmanager
from ipaddress import IPv4Address, IPv4Network
from typing import Any, Optional, Union

from bs4 import BeautifulSoup
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from pydantic import BaseModel
from pydantic.networks import IPvAnyAddress
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing_extensions import Annotated
from uvicorn import run


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = AsyncClient(
        http2=True,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        },
    )
    yield
    await app.state.client.aclose()


app = FastAPI(
    title="IP Checker API",
    description="Check if an IP is hiding something",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    lifespan=lifespan,
)


class Item(BaseModel):
    hiding: bool
    # vpn: bool
    # proxy: bool
    # tor: bool
    # relay: bool
    # hosting: bool


def same_subnet():
    return IPv4Address("1.1.1.1") in IPv4Network("1.1.1.0/24")


def get_summary(soup: BeautifulSoup, column: str) -> str:
    if not (e := soup.find("span", string=column)):
        return ""

    if not (e1 := e.parent.find_next_sibling()):
        return ""

    return e1.get_text().strip().lower()


def get_privacy_detection(soup: BeautifulSoup, column: str) -> Optional[bool]:
    if not (e := soup.find("div", string=column)):
        return None

    if not (e1 := e.find_parent("div")):
        return None

    if not (e2 := e1.find("img")):
        return None

    return "right" in e2.get("src")


async def check_ipinfo(item_id: IPvAnyAddress, request: Request) -> Optional[Item]:
    r = await request.app.state.client.get(f"https://ipinfo.io/{item_id}")

    soup = BeautifulSoup(r.text, "html5lib")

    if not (is_privacy := get_summary(soup, "Privacy")):
        return None

    if not (is_anycast := get_summary(soup, "Anycast")):
        return None

    return Item(hiding="true" in is_privacy or "true" in is_anycast)


@app.get("/check/{item_id}")
async def read_item(item_id: IPvAnyAddress, request: Request) -> Any:
    item = await check_ipinfo(item_id, request)

    if not item:
        return JSONResponse(
            content={"message": "Service Unavailable."}, status_code=500
        )

    return item


# dev only
if __name__ == "__main__":
    run("app:app", host="127.0.0.1", port=1234, reload=True)
