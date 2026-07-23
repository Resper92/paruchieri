from pydantic import BaseModel, ConfigDict


class StaffBase(BaseModel):
    name: str


class StaffCreate(StaffBase):
    salon_id: int


class StaffRead(StaffBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    salon_id: int
