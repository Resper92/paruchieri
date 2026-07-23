from dataclasses import dataclass


@dataclass
class Staff:
    id: int | None
    salon_id: int
    name: str
