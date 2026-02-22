from typing import Iterable
from models.models import Event
from storage.db import get_connection


def insert_events_bulk(events: Iterable[Event]):
    conn = get_connection()
    conn.executemany("""
        INSERT OR IGNORE INTO events
        (date, name, year)
        VALUES (?, ?, ?)
    """, [
        (e.date, e.name, e.year) for e in events
    ])
    conn.commit()