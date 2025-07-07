from typing import Optional

from bs4 import BeautifulSoup


def get_summary(soup: BeautifulSoup, column: str) -> Optional[str]:
    if not (e := soup.find("span", string=column)):
        return None

    if not (e1 := e.parent.find_next_sibling()):
        return None

    return e1.get_text().strip().lower()


def get_range(soup: BeautifulSoup) -> Optional[str]:
    if summary := get_summary(soup, "Range"):
        return summary

    if not (ol := soup.find("ol", {"class": "breadcrumbs"})):
        return None

    if not (links := ol.find_all("a")):
        return None

    return links[-1].get_text().strip()


def get_geolocation(soup: BeautifulSoup) -> Optional[str]:
    if not (e := soup.find("i", {"class": "flag"})):
        return None

    lst: list[str]
    if not (lst := e.get("class")):
        return None

    if not (flt := filter(lambda i: i.startswith("flag-"), lst)):
        return None

    return next(flt, "").replace("flag-", "")
