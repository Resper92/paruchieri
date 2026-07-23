from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppointmentBase(BaseModel):
    start_time: datetime
    end_time: datetime
    status: str = "confirmed"


class AppointmentCreate(AppointmentBase):
    staff_id: int
    service_id: int


class AppointmentRead(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    staff_id: int
    service_id: int
