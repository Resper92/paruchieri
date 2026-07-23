from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.db.base_class import Base


class ServiceModel(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"))
    name = Column(String, nullable=False)
    price = Column(DECIMAL(10, 2))
    duration_minutes = Column(Integer)

    salon = relationship("SalonModel", back_populates="services")
