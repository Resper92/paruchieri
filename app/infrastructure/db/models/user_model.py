from sqlalchemy import Column, Enum, Integer, String

from app.domain.role import Role
from app.infrastructure.db.base_class import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(
        Enum(
            Role,
            name="role",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=Role.CLIENT,
        server_default=Role.CLIENT.value,
    )
