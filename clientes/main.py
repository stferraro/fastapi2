from fastapi import Depends, FastAPI
from scalar_fastapi import get_scalar_api_reference
from sqlmodel.ext.asyncio.session import AsyncSession

from clientes.controllers.cliente_controller import ClienteController
from clientes.database.connection import create_db_and_tables, get_async_session
from clientes.schemas.cliente_schema import ClienteCreate, ClienteRead, ClienteUpdate

app = FastAPI()

# Endpoint de documentación
@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Clientes - Scalar",
    )

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

@app.post("/clientes/", response_model=ClienteRead)
async def crear_cliente(cliente: ClienteCreate, session: AsyncSession = Depends(get_async_session)):
    controller = ClienteController(session)
    return await controller.create_cliente(cliente)

@app.get("/clientes/{cedula}", response_model=ClienteRead)
async def obtener_cliente(cedula: str, session: AsyncSession = Depends(get_async_session)):
    controller = ClienteController(session)
    return await controller.get_cliente(cedula)

@app.get("/clientes/", response_model=list[ClienteRead])
async def obtener_clientes(session: AsyncSession = Depends(get_async_session)):
    controller = ClienteController(session)
    return await controller.get_all_clientes()

@app.put("/clientes/{cliente_id}", response_model=ClienteRead)
async def actualizar_cliente(cliente_id: int, 
                            cliente_update: ClienteUpdate, 
                            session: AsyncSession = Depends(get_async_session)):
    controller = ClienteController(session)
    return await controller.update_cliente(cliente_id, cliente_update)

@app.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: int, session: AsyncSession = Depends(get_async_session)):
    controller = ClienteController(session)
    await controller.delete_cliente(cliente_id)
    return {"detail": "Cliente deleted successfully"}