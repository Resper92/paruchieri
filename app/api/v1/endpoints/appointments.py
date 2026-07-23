from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_appointment_use_case,
    get_book_appointment_use_case,
    get_current_user,
    get_list_appointments_use_case,
)
from app.api.v1.schemas.appointment import AppointmentCreate, AppointmentRead
from app.application.use_cases.appointments import (
    BookAppointmentUseCase,
    GetAppointmentUseCase,
    ListAppointmentsUseCase,
)
from app.domain.entities.user import User

router = APIRouter()


@router.get("/", response_model=list[AppointmentRead])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    use_case: ListAppointmentsUseCase = Depends(get_list_appointments_use_case),
) -> list[AppointmentRead]:
    appointments = use_case.execute(current_user, skip=skip, limit=limit)
    return [AppointmentRead.model_validate(appointment) for appointment in appointments]


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_in: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    use_case: BookAppointmentUseCase = Depends(get_book_appointment_use_case),
) -> AppointmentRead:
    appointment = use_case.execute(
        current_user=current_user,
        staff_id=appointment_in.staff_id,
        service_id=appointment_in.service_id,
        start_time=appointment_in.start_time,
        end_time=appointment_in.end_time,
        status=appointment_in.status,
    )
    return AppointmentRead.model_validate(appointment)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    use_case: GetAppointmentUseCase = Depends(get_appointment_use_case),
) -> AppointmentRead:
    appointment = use_case.execute(current_user, appointment_id)
    return AppointmentRead.model_validate(appointment)
