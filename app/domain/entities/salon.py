from dataclasses import dataclass


@dataclass
class Salon:
    id: int | None
    owner_id: int
    name: str
    address: str | None

    def is_owned_by(self, user_id: int) -> bool:
        return self.owner_id == user_id
