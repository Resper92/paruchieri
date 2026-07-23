from dataclasses import dataclass
from datetime import datetime


@dataclass
class Appointment:
    id: int | None
    client_id: int
    staff_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: str = "confirmed"
