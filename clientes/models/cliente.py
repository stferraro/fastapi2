from typing import Optional

from sqlmodel import Field, SQLModel


class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    last_name: str
    cedula: str = Field(unique=True)
    email: str
    phone: str