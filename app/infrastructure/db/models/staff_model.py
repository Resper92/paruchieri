from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.db.base_class import Base


class StaffModel(Base):
    __tablename__ = "salon_staff"

    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"))
    name = Column(String, nullable=False)

    salon = relationship("SalonModel", back_populates="staff")
