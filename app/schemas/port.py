from pydantic import BaseModel

class PortAdd(BaseModel):
    port: int