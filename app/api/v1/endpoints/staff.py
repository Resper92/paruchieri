from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_create_staff_use_case,
    get_current_user,
    get_list_staff_use_case,
    get_staff_use_case,
)
from app.api.v1.schemas.staff import StaffCreate, StaffRead
from app.application.use_cases.staff import CreateStaffUseCase, GetStaffUseCase, ListStaffUseCase
from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError

router = APIRouter()


@router.get("/", response_model=list[StaffRead])
def list_staff(
    skip: int = 0,
    limit: int = 100,
    salon_id: int | None = None,
    _: User = Depends(get_current_user),
    use_case: ListStaffUseCase = Depends(get_list_staff_use_case),
) -> list[StaffRead]:
    staff = use_case.execute(salon_id=salon_id, skip=skip, limit=limit)
    return [StaffRead.model_validate(member) for member in staff]


@router.post("/", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_in: StaffCreate,
    current_user: User = Depends(get_current_user),
    use_case: CreateStaffUseCase = Depends(get_create_staff_use_case),
) -> StaffRead:
    staff = use_case.execute(current_user=current_user, salon_id=staff_in.salon_id, name=staff_in.name)
    return StaffRead.model_validate(staff)


@router.get("/{staff_id}", response_model=StaffRead)
def get_staff(
    staff_id: int,
    _: User = Depends(get_current_user),
    use_case: GetStaffUseCase = Depends(get_staff_use_case),
) -> StaffRead:
    staff = use_case.execute(staff_id)
    if staff is None:
        raise NotFoundError("Staff member not found")
    return StaffRead.model_validate(staff)
