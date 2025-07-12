from typing import Optional

from bs4 import BeautifulSoup
from fastapi import Request
from pydantic import IPvAnyAddress

from .dependencies import SessionDep
from .models import IpGeolocation, Network, Summary


async def check_ipinfo(
    address: IPvAnyAddress, request: Request, session: SessionDep
) -> Optional[Network]:
    r = await request.app.state.client.get(f"https://ipinfo.io/{address}")
    soup = BeautifulSoup(r.text, "html5lib")

    asn = get_summary(soup, "ASN")
    hostname = get_summary(soup, "Hostname")
    range = get_summary(soup, "Range")
    company = get_summary(soup, "Company")
    hosted_domains = get_summary(soup, "Hosted domains")
    privacy = get_summary(soup, "Privacy")
    anycast = get_summary(soup, "Anycast")
    asn_type = get_summary(soup, "ASN type")
    abuse_contact = get_summary(soup, "Abuse contact")

    city = get_ip_geolocation(soup, "City")
    state = get_ip_geolocation(soup, "State")
    country = get_ip_geolocation(soup, "Country")
    flag = get_flag(soup)
    postal = get_ip_geolocation(soup, "Postal")
    timezone = get_ip_geolocation(soup, "Timezone")
    coordinates = get_ip_geolocation(soup, "Coordinates")

    if not (range and privacy and anycast):
        return None

    is_hiding = "true" in (privacy, anycast)

    new_summary = Summary(
        asn=asn,
        hostname=hostname,
        cidr=range,
        company=company,
        hosted_domains=int(hosted_domains.replace(",", "")) if hosted_domains else None,
        privacy="true" in privacy,
        anycast="true" in anycast,
        asn_type=asn_type,
        abuse_contact=abuse_contact,
    )
    new_ip_geolocation = IpGeolocation(
        city=city,
        state=state,
        country=country,
        flag=flag,
        postal=postal,
        timezone=timezone,
        coordinates=coordinates,
    )
    new_network = Network(
        hiding=is_hiding, summary=new_summary, ipgeolocation=new_ip_geolocation
    )
    session.add(new_network)
    session.commit()
    session.refresh(new_network)

    return new_network


def get_summary(soup: BeautifulSoup, column: str) -> Optional[str]:
    if not (e := soup.find("h2", string="Summary")):
        return None

    if not (e1 := e.find_next("span", string=column)):
        return None

    if not (parent := e1.parent):
        return None

    if not (e2 := parent.find_next_sibling()):
        return None

    return e2.get_text().strip().lower()


def get_ip_geolocation(soup: BeautifulSoup, column: str) -> Optional[str]:
    if not (e := soup.find("h2", string="IP Geolocation")):
        return None

    if not (k := e.find_next("td", string=column)):
        return None

    if not (v := k.find_next_sibling()):
        return None

    return v.get_text().strip()


def get_range(soup: BeautifulSoup) -> Optional[str]:
    if summary := get_summary(soup, "Range"):
        return summary

    if not (ol := soup.find("ol", {"class": "breadcrumbs"})):
        return None

    if not (links := ol.find_all("li")):
        return None

    return links[-1].get_text().strip()


def get_flag(soup: BeautifulSoup) -> Optional[str]:
    if not (e := soup.find("i", {"class": "flag"})):
        return None

    lst: list[str]
    if not (lst := e.get("class")):
        return None

    if not (flt := filter(lambda i: i.startswith("flag-"), lst)):
        return None

    return next(flt, "").replace("flag-", "")
