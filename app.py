from contextlib import asynccontextmanager
from typing import Optional

from bs4 import BeautifulSoup
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic.networks import IPvAnyAddress
from sqlalchemy import literal
from sqlalchemy.dialects.postgresql import INET
from sqlmodel import select
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from src.database import Network
from src.dependencies import SessionDep
from src.ipinfo import get_range, get_summary
from src.models import Item


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    statement = select(Network).where(
        literal(address).cast(INET).op("<<")(Network.cidr)
    )
    return session.exec(statement).first()


async def check_ipinfo(
    address: IPvAnyAddress, request: Request, session: SessionDep
) -> Optional[Network]:
    if known := is_known_network(address, session):
        return known

    r = await request.app.state.client.get(f"https://ipinfo.io/{address}")
    soup = BeautifulSoup(r.text, "html5lib")

    lst = [get_summary(soup, "Privacy"), get_summary(soup, "Anycast")]

    if None in lst:
        return None

    is_hiding = "true" in lst

    if not (range := get_range(soup)):
        return None

    new_network = Network(cidr=range, hiding=is_hiding)
    session.add(new_network)
    session.commit()
    session.refresh(new_network)
    return new_network


@app.get("/check/{address}", response_model=Item)
async def read_item(
    address: IPvAnyAddress, session: SessionDep, request: Request, _: Response
) -> Optional[Network]:
    if not (item := await check_ipinfo(address, request, session)):
        raise HTTPException(503)

    return item
