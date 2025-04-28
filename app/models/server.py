from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    ip_or_domain = Column(String, nullable=False)
    ports = Column(String, nullable=True)

    catalog_statuses = relationship("CatalogStatus", back_populates="server", cascade="all, delete-orphan")
    server_infos = relationship("ServerInfo", back_populates="server", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="server", cascade="all, delete-orphan")
