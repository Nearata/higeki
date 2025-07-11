from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, IPvAnyNetwork
from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import CIDR
from sqlmodel import Field, Relationship, SQLModel


class Item(BaseModel):
    hiding: bool
    created_at: datetime
    updated_at: datetime
    summary: "Summary"


class Network(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hiding: bool
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": func.now()})
    summary: "Summary" = Relationship()


class Summary(SQLModel, table=True):
    network_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="network.id", ondelete="CASCADE")
    asn: Optional[str]
    hostname: Optional[str]
    cidr: Union[str, IPvAnyNetwork] = Field(sa_column=Column(CIDR, index=True))
    company: Optional[str]
    hosted_domains: Optional[int]
    privacy: Optional[bool]
    anycast: Optional[bool]
    asn_type: Optional[str]
    abuse_contact: Optional[str]
