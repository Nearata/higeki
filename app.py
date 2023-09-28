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

from higeki.ipinfo import get_summary
from higeki.models import Item


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
    title="",
    description="",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    lifespan=lifespan,
)


def same_subnet():
    return IPv4Address("1.1.1.1") in IPv4Network("1.1.1.0/24")


async def check_ipinfo(item_id: IPvAnyAddress, request: Request) -> Optional[Item]:
    r = await request.app.state.client.get(f"https://ipinfo.io/{item_id}")

    soup = BeautifulSoup(r.text, "html5lib")

    lst = [get_summary(soup, "Privacy"), get_summary(soup, "Anycast")]

    if None in lst:
        return None

    return Item(hiding="true" in lst)


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
