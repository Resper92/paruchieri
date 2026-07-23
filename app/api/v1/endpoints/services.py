from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_create_service_use_case,
    get_current_user,
    get_list_services_use_case,
    get_service_use_case,
)
from app.api.v1.schemas.service import ServiceCreate, ServiceRead
from app.application.use_cases.services import (
    CreateServiceUseCase,
    GetServiceUseCase,
    ListServicesUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError

router = APIRouter()


@router.get("/", response_model=list[ServiceRead])
def list_services(
    skip: int = 0,
    limit: int = 100,
    salon_id: int | None = None,
    _: User = Depends(get_current_user),
    use_case: ListServicesUseCase = Depends(get_list_services_use_case),
) -> list[ServiceRead]:
    services = use_case.execute(salon_id=salon_id, skip=skip, limit=limit)
    return [ServiceRead.model_validate(service) for service in services]


@router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    current_user: User = Depends(get_current_user),
    use_case: CreateServiceUseCase = Depends(get_create_service_use_case),
) -> ServiceRead:
    service = use_case.execute(
        current_user=current_user,
        salon_id=service_in.salon_id,
        name=service_in.name,
        price=service_in.price,
        duration_minutes=service_in.duration_minutes,
    )
    return ServiceRead.model_validate(service)


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(
    service_id: int,
    _: User = Depends(get_current_user),
    use_case: GetServiceUseCase = Depends(get_service_use_case),
) -> ServiceRead:
    service = use_case.execute(service_id)
    if service is None:
        raise NotFoundError("Service not found")
    return ServiceRead.model_validate(service)
