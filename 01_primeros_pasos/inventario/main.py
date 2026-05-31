from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None ):
    return {"item_id": item_id, "q": q}

@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Inventario - Scalar",
    )

