from dataclasses import dataclass
from typing import Optional

@dataclass
class Holiday:
    date: str
    name: str
    category: str
    country: Optional[str] = None
    years_count: Optional[int] = None
    years_year: Optional[int] = None

@dataclass
class Event:
    date: str
    name: str
    year: Optional[int] = None
