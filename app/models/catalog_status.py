
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class CatalogStatus(Base):
    __tablename__ = "catalog_status"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    port = Column(Integer, nullable=False)
    path = Column(String, nullable=False)
    main_page_status = Column(Integer, nullable=True)
    db_status = Column(Integer, nullable=True)

    server = relationship("Server", back_populates="catalog_statuses")
