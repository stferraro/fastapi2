import pytest
from fastapi import HTTPException
from sqlmodel import select

from clientes.controllers.cliente_controller import ClienteController
from clientes.database.connection import async_session_maker, engine
from clientes.models.cliente import Cliente
from clientes.schemas.cliente_schema import ClienteCreate

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def limpiar_clientes(session):
    clientes = (await session.exec(select(Cliente))).all()
    for c in clientes:
        await session.delete(c)
    await session.commit()


@pytest.fixture
async def session():
    async with async_session_maker() as session:
        await limpiar_clientes(session)
        yield session
        await session.rollback()
    await engine.dispose()

async def test_create_cliente(session):
    controller = ClienteController(session)
    cliente_data = ClienteCreate(
        name="John",
        last_name="Doe",
        cedula="1234567890",
        email="john.doe@example.com",
        phone="555-1234"
    )
    cliente = await controller.create_cliente(cliente_data)
    assert cliente.id is not None
    assert cliente.cedula == "1234567890"

async def test_get_cliente(session):
    controller = ClienteController(session)
    cliente_data = ClienteCreate(
        name="Jane",
        last_name="Smith",
        cedula="0987654321",
        email="jane.smith@example.com",
        phone="555-5678"
    )
    await controller.create_cliente(cliente_data)
    retrieved_cliente = await controller.get_cliente("0987654321")
    assert retrieved_cliente.cedula == "0987654321"
    assert retrieved_cliente.email == "jane.smith@example.com"

async def test_get_all_clientes(session):
    controller = ClienteController(session)
    cliente_data1 = ClienteCreate(
        name="Alice",
        last_name="Johnson",
        cedula="1111111111",
        email="alice.johnson@example.com",
        phone="555-1111"
    )
    cliente_data2 = ClienteCreate(
        name="Bob",
        last_name="Brown",
        cedula="2222222222",
        email="bob.brown@example.com",
        phone="555-2222"
    )
    await controller.create_cliente(cliente_data1)
    await controller.create_cliente(cliente_data2)
    clientes = await controller.get_all_clientes()
    assert len(clientes) == 2

async def test_update_cliente(session):
    controller = ClienteController(session)
    cliente_data = ClienteCreate(
        name="Charlie",
        last_name="Davis",
        cedula="3333333333",
        email="charlie.davis@example.com",
        phone="555-3333"
    )
    created_cliente = await controller.create_cliente(cliente_data)
    updated_cliente = await controller.update_cliente(
        created_cliente.id,
        ClienteCreate(
            name="Charlie",
            last_name="Davis",
            cedula="3333333333",
            email="charlie.davis@example.com",
            phone="555-3331"
        ),
    )
    assert updated_cliente.id == created_cliente.id
    assert updated_cliente.phone == "555-3331"

async def test_delete_cliente(session):
    controller = ClienteController(session)
    cliente_data = ClienteCreate(
        name="David",
        last_name="Evans",
        cedula="4444444444",
        email="david.evans@example.com",
        phone="555-4444"
    )
    created_cliente = await controller.create_cliente(cliente_data)
    await controller.delete_cliente(created_cliente.id)
    with pytest.raises(HTTPException):
        await controller.get_cliente("4444444444")