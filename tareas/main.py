from fastapi import Depends, FastAPI
from scalar_fastapi import get_scalar_api_reference
from sqlmodel.ext.asyncio.session import AsyncSession

from tareas.controllers.tarea_controllers import TareaController
from tareas.database.connection import create_db_and_tables, get_async_session
from tareas.schemas.tareas_schemas import TareaCreate, TareaRead, TareaUpdate

app = FastAPI(title="Tareas API")


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
	return get_scalar_api_reference(
		openapi_url=app.openapi_url,
		title="Tareas - Scalar",
	)


@app.on_event("startup")
async def on_startup():
	await create_db_and_tables()


@app.post("/tareas/", response_model=TareaRead)
async def crear_tarea(
	tarea: TareaCreate,
	session: AsyncSession = Depends(get_async_session),
):
	controller = TareaController(session)
	return await controller.create_tarea(tarea)


@app.get("/tareas/{tarea_id}", response_model=TareaRead)
async def obtener_tarea(
	tarea_id: int,
	session: AsyncSession = Depends(get_async_session),
):
	controller = TareaController(session)
	return await controller.get_tarea(tarea_id)


@app.get("/tareas/", response_model=list[TareaRead])
async def obtener_tareas(session: AsyncSession = Depends(get_async_session)):
	controller = TareaController(session)
	return await controller.get_all_tareas()


@app.put("/tareas/{tarea_id}", response_model=TareaRead)
async def actualizar_tarea(
	tarea_id: int,
	tarea_update: TareaUpdate,
	session: AsyncSession = Depends(get_async_session),
):
	controller = TareaController(session)
	return await controller.update_tarea(tarea_id, tarea_update)


@app.delete("/tareas/{tarea_id}")
async def eliminar_tarea(
	tarea_id: int,
	session: AsyncSession = Depends(get_async_session),
):
	controller = TareaController(session)
	await controller.delete_tarea(tarea_id)
	return {"detail": "Tarea deleted successfully"}
