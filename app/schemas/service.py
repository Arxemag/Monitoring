
from pydantic import BaseModel

class ServiceCreate(BaseModel):
    server_id: int
    port: int
    status: str | None = None

class ServiceUpdate(ServiceCreate):
    pass
