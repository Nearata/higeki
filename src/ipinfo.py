from typing import Optional

from bs4 import BeautifulSoup


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
