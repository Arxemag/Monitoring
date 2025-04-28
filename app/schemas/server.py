from pydantic import BaseModel
from typing import Optional

class ServerCreate(BaseModel):
    name: str
    ip_or_domain: str
    ports: Optional[str] = ""
    meta_info: Optional[str] = ""

class ServerUpdate(ServerCreate):
    pass
