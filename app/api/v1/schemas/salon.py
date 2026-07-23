from pydantic import BaseModel, ConfigDict


class SalonBase(BaseModel):
    name: str
    address: str | None = None


class SalonCreate(SalonBase):
    owner_id: int | None = None


class SalonRead(SalonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
