from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from clientes.models.cliente import Cliente
from clientes.schemas.cliente_schema import ClienteCreate, ClienteRead, ClienteUpdate


class ClienteController:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_cliente(self, cliente_create: ClienteCreate) -> ClienteRead:
        cliente = Cliente.model_validate(cliente_create)
        self.session.add(cliente)
        await self.session.commit()
        await self.session.refresh(cliente)
        return ClienteRead.model_validate(cliente)

    async def get_cliente(self, cedula: str) -> ClienteRead:
        statement = select(Cliente).where(Cliente.cedula == cedula)
        result = await self.session.exec(statement)
        cliente = result.first()
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente not found")
        return ClienteRead.model_validate(cliente)
    
    async def get_all_clientes(self) -> list[ClienteRead]:
        statement = select(Cliente)
        result = await self.session.exec(statement)
        clientes = result.all()
        return [ClienteRead.model_validate(cliente) for cliente in clientes]

    async def update_cliente(self, cliente_id: int, cliente_update: ClienteUpdate) -> ClienteRead:
        cliente = await self.session.get(Cliente, cliente_id)
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente not found")
        
        for key, value in cliente_update.model_dump(exclude_unset=True).items():
            setattr(cliente, key, value)
        
        self.session.add(cliente)
        await self.session.commit()
        await self.session.refresh(cliente)
        return ClienteRead.model_validate(cliente)

    async def delete_cliente(self, cliente_id: int) -> None:
        cliente = await self.session.get(Cliente, cliente_id)
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente not found")
        
        await self.session.delete(cliente)
        await self.session.commit()