from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)

    server_id = Column(Integer, ForeignKey("servers.id"))  # ✅ привязка к Server
    server = relationship("Server", back_populates="services")  # ✅ обратная связь
