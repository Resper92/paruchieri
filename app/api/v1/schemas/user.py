from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.role import Role


class UserBase(BaseModel):
    email: EmailStr
    role: Role = Role.CLIENT


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RoleUpdate(BaseModel):
    role: Role
