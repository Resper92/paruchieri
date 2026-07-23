from sqlalchemy.orm import Session

from app.domain.entities.service import Service
from app.infrastructure.db.models.service_model import ServiceModel


class SqlAlchemyServiceRepository:
    """Infrastructure adapter implementing the ServiceRepository port."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, service_id: int) -> Service | None:
        model = self._db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        return self._to_entity(model) if model else None

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Service]:
        models = self._db.query(ServiceModel).offset(skip).limit(limit).all()
        return [self._to_entity(model) for model in models]

    def get_multi_by_salon(self, salon_id: int, skip: int = 0, limit: int = 100) -> list[Service]:
        models = (
            self._db.query(ServiceModel)
            .filter(ServiceModel.salon_id == salon_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def add(self, service: Service) -> Service:
        model = ServiceModel(
            salon_id=service.salon_id,
            name=service.name,
            price=service.price,
            duration_minutes=service.duration_minutes,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ServiceModel) -> Service:
        return Service(
            id=model.id,
            salon_id=model.salon_id,
            name=model.name,
            price=model.price,
            duration_minutes=model.duration_minutes,
        )
