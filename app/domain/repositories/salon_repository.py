from typing import Protocol

from app.domain.entities.salon import Salon


class SalonRepository(Protocol):
    def get(self, salon_id: int) -> Salon | None: ...

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Salon]: ...

    def add(self, salon: Salon) -> Salon: ...
