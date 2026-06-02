from datetime import date

import pytest
from sqlmodel import select

from tareas.database.connection import async_session_maker, create_db_and_tables, engine
from tareas.models.tarea import Tarea

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
	return "asyncio"


async def limpiar_tareas(session):
	tareas = (await session.exec(select(Tarea))).all()
	for tarea in tareas:
		await session.delete(tarea)
	await session.commit()


@pytest.fixture
async def session():
	await create_db_and_tables()
	async with async_session_maker() as session:
		await limpiar_tareas(session)
		yield session
		await limpiar_tareas(session)
	await engine.dispose()


async def test_create_tarea(session):
	tarea = Tarea(
		nombre="Preparar entrega",
		descripcion="Organizar tareas pendientes",
		fecha_inicio=date(2026, 5, 31),
	)

	session.add(tarea)
	await session.commit()
	await session.refresh(tarea)

	assert tarea.id is not None
	assert tarea.nombre == "Preparar entrega"
	assert tarea.descripcion == "Organizar tareas pendientes"
	assert tarea.fecha_inicio == date(2026, 5, 31)


async def test_get_tarea(session):
	tarea = Tarea(
		nombre="Estudiar SQLModel",
		descripcion="Repasar modelos y schemas",
		fecha_inicio=date(2026, 6, 1),
	)

	session.add(tarea)
	await session.commit()

	result = await session.exec(select(Tarea).where(Tarea.nombre == "Estudiar SQLModel"))
	tarea_guardada = result.one()

	assert tarea_guardada.id is not None
	assert tarea_guardada.descripcion == "Repasar modelos y schemas"
	assert tarea_guardada.fecha_inicio == date(2026, 6, 1)
