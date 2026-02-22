import sqlite3

DB_FILE = "holidays.db"

_conn: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_FILE)
        _conn.row_factory = sqlite3.Row
    return _conn


def close_connection():
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS holidays (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            country TEXT,
            years_count INTEGER,
            years_year INTEGER,
            UNIQUE(date, name, category, country)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            year INTEGER,
            UNIQUE(date, name)
        )
    """)

    conn.commit()