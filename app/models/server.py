from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    host = Column(String, nullable=False)
    ports = Column(String, nullable=True)

    # Связи
    info = relationship("ServerInfo", back_populates="server", uselist=False)
    catalogs = relationship("CatalogStatus", back_populates="server")
    services = relationship("Service", back_populates="server")  # ✅ добавлено!

class ServerInfo(Base):
    __tablename__ = "server_info"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)

    registration_number = Column(String, nullable=True)
    expiration_date = Column(String, nullable=True)
    license_limit = Column(Integer, nullable=True)
    sessions_count = Column(Integer, nullable=True)
    backup_time = Column(String, nullable=True)
    restart_time = Column(String, nullable=True)

    server = relationship("Server", back_populates="info")
