from contextlib import asynccontextmanager
from ipaddress import IPv4Address, IPv4Network
from typing import Union

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
    version="1.0.0",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    lifespan=lifespan,
)


def same_subnet():
    return IPv4Address("1.1.1.1") in IPv4Network("1.1.1.0/24")


async def check_ipinfo(item_id: IPvAnyAddress, request: Request):
    r = await request.app.state.client.get(f"https://ipinfo.io/{item_id}")
    soup = BeautifulSoup(r.text, "html5lib")

    e = soup.find("span", string="Privacy")

    if not e:
        return None

    e1 = e.find_parent("tr")

    if not e1:
        return None

    print("true" in e1.get_text().lower())


@app.get("/items/{item_id}")
async def read_item(item_id: IPvAnyAddress, request: Request):
    data = await check_ipinfo(item_id, request)
    return {"hiding": True}


# dev only
if __name__ == "__main__":
    run("app:app", host="127.0.0.1", port=1234, reload=True)
