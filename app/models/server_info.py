from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ServerInfo(Base):
    __tablename__ = "server_info"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    port = Column(Integer, nullable=False)
    registration_number = Column(Integer, nullable=True)
    expiration_date = Column(Date, nullable=True)
    license_limit = Column(Integer, nullable=True)
    sessions_count = Column(Integer, nullable=True)
    backup_time = Column(String, nullable=True)
    restart_time = Column(String, nullable=True)

    server = relationship("Server", back_populates="server_infos")
