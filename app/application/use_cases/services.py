from decimal import Decimal

from app.domain.entities.service import Service
from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError
from app.domain.policies import ensure_can_manage_salon, ensure_role
from app.domain.repositories.salon_repository import SalonRepository
from app.domain.repositories.service_repository import ServiceRepository
from app.domain.role import Role


class CreateServiceUseCase:
    def __init__(
        self, service_repository: ServiceRepository, salon_repository: SalonRepository
    ) -> None:
        self._services = service_repository
        self._salons = salon_repository

    def execute(
        self,
        current_user: User,
        salon_id: int,
        name: str,
        price: Decimal | None,
        duration_minutes: int | None,
    ) -> Service:
        ensure_role(current_user, Role.PARRUCCHIERE, Role.SUPERADMIN)

        salon = self._salons.get(salon_id)
        if salon is None:
            raise NotFoundError("Salon not found")
        ensure_can_manage_salon(current_user, salon)

        service = Service(
            id=None, salon_id=salon_id, name=name, price=price, duration_minutes=duration_minutes
        )
        return self._services.add(service)


class ListServicesUseCase:
    def __init__(self, service_repository: ServiceRepository) -> None:
        self._services = service_repository

    def execute(self, salon_id: int | None, skip: int = 0, limit: int = 100) -> list[Service]:
        if salon_id is not None:
            return self._services.get_multi_by_salon(salon_id, skip=skip, limit=limit)
        return self._services.get_multi(skip=skip, limit=limit)


class GetServiceUseCase:
    def __init__(self, service_repository: ServiceRepository) -> None:
        self._services = service_repository

    def execute(self, service_id: int) -> Service | None:
        return self._services.get(service_id)
