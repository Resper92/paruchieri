from app.domain.entities.salon import Salon
from app.domain.entities.user import User
from app.domain.policies import ensure_role
from app.domain.repositories.salon_repository import SalonRepository
from app.domain.role import Role


class CreateSalonUseCase:
    def __init__(self, salon_repository: SalonRepository) -> None:
        self._salons = salon_repository

    def execute(
        self, current_user: User, name: str, address: str | None, owner_id: int | None
    ) -> Salon:
        ensure_role(current_user, Role.PARRUCCHIERE, Role.SUPERADMIN)

        resolved_owner_id = current_user.id
        if current_user.role == Role.SUPERADMIN and owner_id is not None:
            resolved_owner_id = owner_id

        salon = Salon(id=None, owner_id=resolved_owner_id, name=name, address=address)
        return self._salons.add(salon)


class ListSalonsUseCase:
    def __init__(self, salon_repository: SalonRepository) -> None:
        self._salons = salon_repository

    def execute(self, skip: int = 0, limit: int = 100) -> list[Salon]:
        return self._salons.get_multi(skip=skip, limit=limit)


class GetSalonUseCase:
    def __init__(self, salon_repository: SalonRepository) -> None:
        self._salons = salon_repository

    def execute(self, salon_id: int) -> Salon | None:
        return self._salons.get(salon_id)
