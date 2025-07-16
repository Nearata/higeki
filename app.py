from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from httpx import AsyncClient
from pydantic.networks import IPvAnyAddress
from sqlalchemy import literal
from sqlalchemy.dialects.postgresql import INET
from sqlmodel import select
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from src.dependencies import SessionDep
from src.ipinfo import check_ipinfo
from src.models import Item, Network, Summary


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
    statement = (
        select(Network)
        .join(Summary)
        .where(literal(address).cast(INET).op("<<")(Summary.cidr))
    )
    return session.exec(statement).first()


@app.get("/check/{address}", response_model=Item)
async def read_item(
    address: IPvAnyAddress, session: SessionDep, request: Request, _: Response
) -> Optional[Network]:
    if known := is_known_network(address, session):
        return known

    if not (item := await check_ipinfo(address, request, session)):
        raise HTTPException(503, "Unable to retrieve data. Please try again later.")

    return item
