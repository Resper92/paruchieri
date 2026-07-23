from sqlalchemy.orm import Session

from app.domain.entities.appointment import Appointment
from app.infrastructure.db.models.appointment_model import AppointmentModel
from app.infrastructure.db.models.salon_model import SalonModel
from app.infrastructure.db.models.staff_model import StaffModel


class SqlAlchemyAppointmentRepository:
    """Infrastructure adapter implementing the AppointmentRepository port."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, appointment_id: int) -> Appointment | None:
        model = self._db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
        return self._to_entity(model) if model else None

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        models = self._db.query(AppointmentModel).offset(skip).limit(limit).all()
        return [self._to_entity(model) for model in models]

    def get_for_client(self, client_id: int, skip: int = 0, limit: int = 100) -> list[Appointment]:
        models = (
            self._db.query(AppointmentModel)
            .filter(AppointmentModel.client_id == client_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def get_for_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> list[Appointment]:
        models = (
            self._db.query(AppointmentModel)
            .join(StaffModel, AppointmentModel.staff_id == StaffModel.id)
            .join(SalonModel, StaffModel.salon_id == SalonModel.id)
            .filter(SalonModel.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def add(self, appointment: Appointment) -> Appointment:
        model = AppointmentModel(
            client_id=appointment.client_id,
            staff_id=appointment.staff_id,
            service_id=appointment.service_id,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: AppointmentModel) -> Appointment:
        return Appointment(
            id=model.id,
            client_id=model.client_id,
            staff_id=model.staff_id,
            service_id=model.service_id,
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
        )
