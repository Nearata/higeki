from ipaddress import ip_address as ipaddress_validator
from re import sub
from typing import Any, Optional

import strawberry
from sqlalchemy import inspect, literal
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import load_only, raiseload, selectinload
from sqlalchemy.orm.state import InstanceState
from sqlmodel import select
from strawberry.fastapi import GraphQLRouter

from src.dependencies import graphql_context
from src.ipinfo import check_ipinfo
from src.models import IpGeolocation as IpGeolocationModel
from src.models import Network as NetworkModel
from src.models import Summary as SummaryModel


def snakecase(s: str) -> str:
    return sub(r"[A-Z]", lambda i: f"_{i.group().lower()}", s)


class Models:
    network = NetworkModel
    summary = SummaryModel
    ipgeolocation = IpGeolocationModel


@strawberry.experimental.pydantic.type(model=NetworkModel)
class Network:
    hiding: Optional[bool]


@strawberry.experimental.pydantic.type(model=SummaryModel)
class Summary:
    asn: Optional[str]
    hostname: Optional[str]
    cidr: Optional[str]
    company: Optional[str]
    hosted_domains: Optional[int]
    privacy: Optional[bool]
    anycast: Optional[bool]
    asn_type: Optional[str]
    abuse_contact: Optional[str]


@strawberry.experimental.pydantic.type(model=IpGeolocationModel)
class IpGeolocation:
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    flag: Optional[str]
    postal: Optional[str]
    timezone: Optional[str]
    coordinates: Optional[str]


@strawberry.type
class Response:
    network: "Network"
    summary: Optional["Summary"]
    ipGeolocation: Optional["IpGeolocation"]

    @classmethod
    def from_models(cls, network: NetworkModel) -> "Response":
        state: InstanceState[Any] = inspect(network, True)
        unloaded = state.unloaded
        return cls(
            network=Network.from_pydantic(network),
            summary=Summary.from_pydantic(network.summary)
            if "summary" not in unloaded
            else None,
            ipGeolocation=IpGeolocation.from_pydantic(network.ipgeolocation)
            if "ipgeolocation" not in unloaded
            else None,
        )


@strawberry.type
class Query:
    @strawberry.field
    async def query(self, info: strawberry.Info, ip_address: str) -> Optional[Response]:
        try:
            address = ipaddress_validator(ip_address)
        except ValueError as e:
            raise e

        o: list[Any] = []

        for i in info.selected_fields[0].selections:
            table = i.name.lower()

            out: list[Any] = []
            relationship = None
            for i1 in i.selections:
                column = snakecase(i1.name)

                if table == "network":
                    out.append(getattr(NetworkModel, column))
                else:
                    relationship = getattr(Models, table)
                    out.append(getattr(relationship, column))

            if relationship:
                o.append(
                    selectinload(getattr(NetworkModel, table)).load_only(
                        *(i for i in out)
                    )
                )
            else:
                o.append(load_only(*(i for i in out)))

        request = info.context["request"]
        session = info.context["session"]

        statement = (
            select(NetworkModel)
            .join(SummaryModel)
            .where(literal(ip_address).cast(INET).op("<<")(SummaryModel.cidr))
            .options(raiseload("*"), *o)
        )

        if known := session.exec(statement).first():
            return Response.from_models(known)

        if r := await check_ipinfo(address, request, session):
            return Response.from_models(r)

        raise Exception("Unable to retrieve data. Please try again later.")


schema = strawberry.Schema(Query)

graphql_app = GraphQLRouter(schema, context_getter=graphql_context)
