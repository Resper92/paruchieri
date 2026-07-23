from sqlalchemy.orm import Session

from app.domain.entities.salon import Salon
from app.infrastructure.db.models.salon_model import SalonModel


class SqlAlchemySalonRepository:
    """Infrastructure adapter implementing the SalonRepository port."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, salon_id: int) -> Salon | None:
        model = self._db.query(SalonModel).filter(SalonModel.id == salon_id).first()
        return self._to_entity(model) if model else None

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Salon]:
        models = self._db.query(SalonModel).offset(skip).limit(limit).all()
        return [self._to_entity(model) for model in models]

    def add(self, salon: Salon) -> Salon:
        model = SalonModel(owner_id=salon.owner_id, name=salon.name, address=salon.address)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: SalonModel) -> Salon:
        return Salon(id=model.id, owner_id=model.owner_id, name=model.name, address=model.address)
