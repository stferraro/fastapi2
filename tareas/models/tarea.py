from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Tarea(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	nombre: str
	descripcion: Optional[str] = None
	fecha_inicio: date
