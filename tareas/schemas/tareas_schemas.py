from datetime import date
from typing import Optional

from sqlmodel import SQLModel


class TareaBase(SQLModel):
	nombre: str
	descripcion: Optional[str] = None
	fecha_inicio: date


class TareaCreate(TareaBase):
	pass


class TareaRead(TareaBase):
	id: int


class TareaUpdate(SQLModel):
	nombre: Optional[str] = None
	descripcion: Optional[str] = None
	fecha_inicio: Optional[date] = None
