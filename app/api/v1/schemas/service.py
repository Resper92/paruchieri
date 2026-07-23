from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    price: Decimal | None = None
    duration_minutes: int | None = None


class ServiceCreate(ServiceBase):
    salon_id: int


class ServiceRead(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    salon_id: int
