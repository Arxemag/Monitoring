from pydantic import BaseModel
from typing import Optional, List

# --- SERVER ---
class ServerBase(BaseModel):
    name: str
    url: str

class ServerCreate(ServerBase):
    pass

class ServerUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None

class ServerInfoRead(ServerBase):
    id: int
    ports: Optional[str] = None  # если порты храним строкой

    class Config:
        orm_mode = True

# --- SERVICE ---
class ServiceBase(BaseModel):
    name: str
    port: int

class ServiceCreate(ServiceBase):
    server_id: int

class ServiceInfoRead(ServiceBase):
    id: int
    server_id: int

    class Config:
        orm_mode = True
