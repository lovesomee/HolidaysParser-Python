from playwright.sync_api import Page
from typing import List
from models.models import Holiday, Event
import re


def parse_holidays(page: Page, url: str, iso_date: str) -> List[Holiday]:
    page.goto(url, timeout=90000)
    page.wait_for_selector("div.listing_wr", timeout=90000)
    page.wait_for_timeout(2000)

    container = page.query_selector("div.listing_wr")
    if not container:
        return []

    all_divs = container.query_selector_all("div")
    holidays: List[Holiday] = []
    seen = set()
    category = "general"

    for div in all_divs:
        cls = div.get_attribute("class") or ""
        div_id = div.get_attribute("id") or ""

        if "hr-hr_vesna" in cls:
            if category == "general":
                category = "orthodox"
            elif category in ["orthodox", "national"]:
                category = "name_day"
            continue

        if div_id in ["prin", "national", "nat_in"]:
            category = "national"
            continue

        span = div.query_selector("span[itemprop='text']")
        if not span:
            continue

        text = span.inner_text().strip()
        if not text or text in seen:
            continue

        if category == "name_day":
            if not text.startswith("Именины у"):
                continue

            text = text.split("Источник:", 1)[0].strip()

        seen.add(text)

        country = None
        if category == "national":
            parts = text.rsplit(" - ", 1)
            if len(parts) == 2:
                text = parts[0].strip()
                country = parts[1].strip()

        holidays.append(Holiday(
            date=iso_date,
            name=text,
            category=category,
            country=country
        ))

    return holidays


def parse_events(page: Page, iso_date: str) -> List[Event]:
    events: List[Event] = []

    block = page.query_selector("div.event_block.adv")
    if not block:
        return events

    items = block.query_selector_all("div.event")

    for item in items:
        text = item.inner_text().strip()
        if not text:
            continue

        text = text.lstrip("•").strip()

        match = re.match(r"\d+\s+\S+\s+(\d{4})\s+года\s+(.+)", text)
        if not match:
            continue

        year = int(match.group(1))
        name = match.group(2).strip()

        events.append(Event(
            date=iso_date,
            name=name,
            year=year
        ))

    return events
