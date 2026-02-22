from typing import Iterable
from models.models import Holiday
from storage.db import get_connection


def insert_holidays_bulk(holidays: Iterable[Holiday]):
    conn = get_connection()
    conn.executemany("""
        INSERT OR IGNORE INTO holidays
        (date, name, category, country, years_count, years_year)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (
            h.date,
            h.name,
            h.category,
            h.country,
            h.years_count,
            h.years_year
        ) for h in holidays
    ])
    conn.commit()