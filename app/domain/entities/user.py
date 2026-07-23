from dataclasses import dataclass

from app.domain.role import Role


@dataclass
class User:
    id: int | None
    email: str
    password_hash: str
    role: Role

    def has_any_role(self, *roles: Role) -> bool:
        return self.role in roles
