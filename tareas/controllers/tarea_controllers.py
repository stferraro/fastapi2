from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from tareas.models.tarea import Tarea
from tareas.schemas.tareas_schemas import TareaCreate, TareaRead, TareaUpdate


class TareaController:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def create_tarea(self, tarea_create: TareaCreate) -> TareaRead:
		tarea = Tarea.model_validate(tarea_create)
		self.session.add(tarea)
		await self.session.commit()
		await self.session.refresh(tarea)
		return TareaRead.model_validate(tarea)

	async def get_tarea(self, tarea_id: int) -> TareaRead:
		tarea = await self.session.get(Tarea, tarea_id)
		if tarea is None:
			raise HTTPException(status_code=404, detail="Tarea not found")
		return TareaRead.model_validate(tarea)

	async def get_all_tareas(self) -> list[TareaRead]:
		statement = select(Tarea)
		result = await self.session.exec(statement)
		tareas = result.all()
		return [TareaRead.model_validate(tarea) for tarea in tareas]

	async def update_tarea(self, tarea_id: int, tarea_update: TareaUpdate) -> TareaRead:
		tarea = await self.session.get(Tarea, tarea_id)
		if tarea is None:
			raise HTTPException(status_code=404, detail="Tarea not found")

		for key, value in tarea_update.model_dump(exclude_unset=True).items():
			setattr(tarea, key, value)

		self.session.add(tarea)
		await self.session.commit()
		await self.session.refresh(tarea)
		return TareaRead.model_validate(tarea)

	async def delete_tarea(self, tarea_id: int) -> None:
		tarea = await self.session.get(Tarea, tarea_id)
		if tarea is None:
			raise HTTPException(status_code=404, detail="Tarea not found")

		await self.session.delete(tarea)
		await self.session.commit()
