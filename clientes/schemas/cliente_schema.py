from typing import Optional

from sqlmodel import SQLModel


class ClienteBase(SQLModel):
    name: str
    last_name: str
    cedula: str
    email: str
    phone: str

class ClienteCreate(ClienteBase):
    pass

class ClienteRead(ClienteBase):
    id: int

class ClienteUpdate(SQLModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    cedula: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
