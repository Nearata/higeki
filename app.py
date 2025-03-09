from contextlib import asynccontextmanager
from ipaddress import ip_address, ip_network
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
from src.ipinfo import get_geolocation, get_summary
from src.models import Item


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
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


def is_known_network(address: IPvAnyAddress, session: SessionDep) -> Optional[Item]:
    networks = session.exec(select(Network)).all()

    if known := list(
        filter(lambda i: ip_address(address) in ip_network(i.address), networks)
    ):
        return Item(hiding=known[0].hiding, flag=known[0].flag)

    return None


async def check_ipinfo(
    item_id: IPvAnyAddress, request: Request, session: SessionDep
) -> Optional[Item]:
    r = await request.app.state.client.get(f"https://ipinfo.io/{item_id}")

    soup = BeautifulSoup(r.text, "html5lib")

    lst = [get_summary(soup, "Privacy"), get_summary(soup, "Anycast")]

    if None in lst:
        return None

    is_hiding = "true" in lst

    if not (network := get_summary(soup, "Range")):
        return None

    if not (geo := get_geolocation(soup)):
        return None

    networks = session.exec(select(Network)).all()

    if network not in list(map(lambda i: i.address, networks)):
        new_network = Network(address=network, hiding=is_hiding, flag=geo)
        session.add(new_network)
        session.commit()
        session.refresh(new_network)

    return Item(hiding=is_hiding, flag=geo)


@app.get("/check/{address}")
async def read_item(
    address: IPvAnyAddress, session: SessionDep, request: Request, response: Response
) -> Optional[Item]:
    if known := is_known_network(address, session):
        return known

    item = await check_ipinfo(address, request, session)

    if not item:
        raise HTTPException(503)
        # return Response(status_code=503)

    response.status_code = 201

    return item


# dev only
if __name__ == "__main__":
    run("app:app", host="127.0.0.1", port=1234, reload=True)
