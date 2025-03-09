from typing import Optional

from bs4 import BeautifulSoup


def get_privacy_detection(soup: BeautifulSoup, column: str) -> Optional[bool]:
    if not (e := soup.find("div", string=column)):
        return None

    if not (e1 := e.find_parent("div")):
        return None

    if not (e2 := e1.find("img")):
        return None

    return "right" in e2.get("src")


def get_summary(soup: BeautifulSoup, column: str) -> Optional[str]:
    if not (e := soup.find("span", string=column)):
        return None

    if not (e1 := e.parent.find_next_sibling()):
        return None

    return e1.get_text().strip().lower()


def get_geolocation(soup: BeautifulSoup) -> Optional[str]:
    if not (e := soup.find("i", class_="flag")):
        return None

    lst: list[str]
    if not (lst := e.get("class")):
        return None

    if not (flt := filter(lambda i: i.startswith("flag-"), lst)):
        return None

    return next(flt, "").replace("flag-", "")
