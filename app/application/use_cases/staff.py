from app.domain.entities.staff import Staff
from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError
from app.domain.policies import ensure_can_manage_salon, ensure_role
from app.domain.repositories.salon_repository import SalonRepository
from app.domain.repositories.staff_repository import StaffRepository
from app.domain.role import Role


class CreateStaffUseCase:
    def __init__(self, staff_repository: StaffRepository, salon_repository: SalonRepository) -> None:
        self._staff = staff_repository
        self._salons = salon_repository

    def execute(self, current_user: User, salon_id: int, name: str) -> Staff:
        ensure_role(current_user, Role.PARRUCCHIERE, Role.SUPERADMIN)

        salon = self._salons.get(salon_id)
        if salon is None:
            raise NotFoundError("Salon not found")
        ensure_can_manage_salon(current_user, salon)

        return self._staff.add(Staff(id=None, salon_id=salon_id, name=name))


class ListStaffUseCase:
    def __init__(self, staff_repository: StaffRepository) -> None:
        self._staff = staff_repository

    def execute(self, salon_id: int | None, skip: int = 0, limit: int = 100) -> list[Staff]:
        if salon_id is not None:
            return self._staff.get_multi_by_salon(salon_id, skip=skip, limit=limit)
        return self._staff.get_multi(skip=skip, limit=limit)


class GetStaffUseCase:
    def __init__(self, staff_repository: StaffRepository) -> None:
        self._staff = staff_repository

    def execute(self, staff_id: int) -> Staff | None:
        return self._staff.get(staff_id)
