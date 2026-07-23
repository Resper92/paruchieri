from datetime import datetime

from app.domain.entities.appointment import Appointment
from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError, PermissionDeniedError
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.role import Role


class BookAppointmentUseCase:
    def __init__(self, appointment_repository: AppointmentRepository) -> None:
        self._appointments = appointment_repository

    def execute(
        self,
        current_user: User,
        staff_id: int,
        service_id: int,
        start_time: datetime,
        end_time: datetime,
        status: str = "confirmed",
    ) -> Appointment:
        appointment = Appointment(
            id=None,
            client_id=current_user.id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status=status,
        )
        return self._appointments.add(appointment)


class ListAppointmentsUseCase:
    def __init__(self, appointment_repository: AppointmentRepository) -> None:
        self._appointments = appointment_repository

    def execute(self, current_user: User, skip: int = 0, limit: int = 100) -> list[Appointment]:
        if current_user.role == Role.SUPERADMIN:
            return self._appointments.get_multi(skip=skip, limit=limit)
        if current_user.role == Role.PARRUCCHIERE:
            return self._appointments.get_for_owner(current_user.id, skip=skip, limit=limit)
        return self._appointments.get_for_client(current_user.id, skip=skip, limit=limit)


class GetAppointmentUseCase:
    def __init__(self, appointment_repository: AppointmentRepository) -> None:
        self._appointments = appointment_repository

    def execute(self, current_user: User, appointment_id: int) -> Appointment:
        appointment = self._appointments.get(appointment_id)
        if appointment is None:
            raise NotFoundError("Appointment not found")
        if current_user.role == Role.CLIENT and appointment.client_id != current_user.id:
            raise PermissionDeniedError("Not your appointment")
        return appointment
