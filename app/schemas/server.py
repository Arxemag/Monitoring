
from pydantic import BaseModel

class ServerCreate(BaseModel):
    name: str
    ip_or_domain: str
    ports: str
    is_active: bool = True
    meta_info: str | None = None

class ServerUpdate(ServerCreate):
    pass
