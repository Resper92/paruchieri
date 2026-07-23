from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_create_salon_use_case,
    get_current_user,
    get_list_salons_use_case,
    get_salon_use_case,
)
from app.api.v1.schemas.salon import SalonCreate, SalonRead
from app.application.use_cases.salons import CreateSalonUseCase, GetSalonUseCase, ListSalonsUseCase
from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError

router = APIRouter()


@router.get("/", response_model=list[SalonRead])
def list_salons(
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_user),
    use_case: ListSalonsUseCase = Depends(get_list_salons_use_case),
) -> list[SalonRead]:
    salons = use_case.execute(skip=skip, limit=limit)
    return [SalonRead.model_validate(salon) for salon in salons]


@router.post("/", response_model=SalonRead, status_code=status.HTTP_201_CREATED)
def create_salon(
    salon_in: SalonCreate,
    current_user: User = Depends(get_current_user),
    use_case: CreateSalonUseCase = Depends(get_create_salon_use_case),
) -> SalonRead:
    salon = use_case.execute(
        current_user=current_user,
        name=salon_in.name,
        address=salon_in.address,
        owner_id=salon_in.owner_id,
    )
    return SalonRead.model_validate(salon)


@router.get("/{salon_id}", response_model=SalonRead)
def get_salon(
    salon_id: int,
    _: User = Depends(get_current_user),
    use_case: GetSalonUseCase = Depends(get_salon_use_case),
) -> SalonRead:
    salon = use_case.execute(salon_id)
    if salon is None:
        raise NotFoundError("Salon not found")
    return SalonRead.model_validate(salon)
