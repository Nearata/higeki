from contextlib import asynccontextmanager
from ipaddress import ip_network
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic.networks import IPvAnyAddress
from sqlmodel import select
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from uvicorn import run

from src.database import Network, create_db_and_tables
from src.dependencies import SessionDep
from src.ipinfo import get_geolocation, get_range_from_breadcrumb, get_summary
from src.models import Item


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("data").mkdir(exist_ok=True)
    create_db_and_tables()
    app.state.client = AsyncClient(
        http2=True,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
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


def is_known_network(address: IPvAnyAddress, session: SessionDep) -> Optional[Network]:
    address1 = int(address)
    statement = select(Network).where(
        Network.network <= address1, Network.broadcast >= address1
    )
    return session.exec(statement).first()


async def check_ipinfo(
    address: IPvAnyAddress, request: Request, session: SessionDep
) -> Optional[Network]:
    r = await request.app.state.client.get(f"https://ipinfo.io/{address}")

    soup = BeautifulSoup(r.text, "html5lib")

    lst = [get_summary(soup, "Privacy"), get_summary(soup, "Anycast")]

    if None in lst:
        return None

    is_hiding = "true" in lst

    if not (range := (get_summary(soup, "Range") or get_range_from_breadcrumb(soup))):
        return None

    cidr = ip_network(range, False)
    network = int(cidr.network_address)
    broadcast = int(cidr.broadcast_address)

    statement = select(Network).where(Network.cidr == range)

    if not (result := session.exec(statement).first()):
        geo = get_geolocation(soup)
        new_network = Network(
            cidr=range, network=network, broadcast=broadcast, hiding=is_hiding, flag=geo
        )
        session.add(new_network)
        session.commit()
        session.refresh(new_network)
        return new_network

    return result


@app.get("/check/{address}", response_model=Item)
async def read_item(
    address: IPvAnyAddress, session: SessionDep, request: Request, response: Response
) -> Optional[Network]:
    if known := is_known_network(address, session):
        return known

    item = await check_ipinfo(address, request, session)

    if not item:
        raise HTTPException(503)

    return item


# dev only
if __name__ == "__main__":
    run("app:app", host="127.0.0.1", port=8000, reload=True)
