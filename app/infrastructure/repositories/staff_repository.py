from sqlalchemy.orm import Session

from app.domain.entities.staff import Staff
from app.infrastructure.db.models.staff_model import StaffModel


class SqlAlchemyStaffRepository:
    """Infrastructure adapter implementing the StaffRepository port."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, staff_id: int) -> Staff | None:
        model = self._db.query(StaffModel).filter(StaffModel.id == staff_id).first()
        return self._to_entity(model) if model else None

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Staff]:
        models = self._db.query(StaffModel).offset(skip).limit(limit).all()
        return [self._to_entity(model) for model in models]

    def get_multi_by_salon(self, salon_id: int, skip: int = 0, limit: int = 100) -> list[Staff]:
        models = (
            self._db.query(StaffModel)
            .filter(StaffModel.salon_id == salon_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def add(self, staff: Staff) -> Staff:
        model = StaffModel(salon_id=staff.salon_id, name=staff.name)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: StaffModel) -> Staff:
        return Staff(id=model.id, salon_id=model.salon_id, name=model.name)
