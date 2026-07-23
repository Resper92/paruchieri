from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.infrastructure.db.base_class import Base


class SalonModel(Base):
    __tablename__ = "salons"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    address = Column(Text)

    staff = relationship("StaffModel", back_populates="salon")
    services = relationship("ServiceModel", back_populates="salon")
