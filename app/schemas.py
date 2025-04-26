from pydantic import BaseModel
from datetime import date
from typing import Optional

class ServerInfoBase(BaseModel):
    registration_number: Optional[int] = None
    expiration_date: Optional[date] = None
    reg_file_limit: Optional[int] = None
    session_count: Optional[int] = None
    backup_time: Optional[str] = None
    restart_time: Optional[str] = None

class ServerInfoCreate(ServerInfoBase):
    pass

class ServerInfoUpdate(ServerInfoBase):
    pass

class ServerInfoRead(ServerInfoBase):
    id: int
    server_id: int

    class Config:
        from_attributes = True

# --- Новые схемы для каталога статуса ---
class CatalogStatusBase(BaseModel):
    path: str
    main_page_status: Optional[int] = None
    db_status: Optional[int] = None

class CatalogStatusCreate(CatalogStatusBase):
    server_id: int

class CatalogStatusUpdate(CatalogStatusBase):
    pass

class CatalogStatusRead(CatalogStatusBase):
    id: int
    server_id: int

    class Config:
        from_attributes = True
