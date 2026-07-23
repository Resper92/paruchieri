from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Service:
    id: int | None
    salon_id: int
    name: str
    price: Decimal | None
    duration_minutes: int | None
