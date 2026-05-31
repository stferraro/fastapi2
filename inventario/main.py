from fastapi import FastAPI, HTTPException
from inventario.schemas.product_schema import ProductCreate, ProductResponse
from inventario.database.connection import create_tables
from inventario.controllers.product_controller import (
    add_product_controller,
    list_products_controller,
    get_product_controller,
    delete_product_controller
)

from scalar_fastapi import get_scalar_api_reference

app = FastAPI(title="Inventario API")
create_tables()

# Endpoint de documentación
@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Inventario - Scalar",
    )

@app.post("/products", response_model=dict)
def create_product(product: ProductCreate):
    return add_product_controller(
        product.product_code, product.name, product.price_unit, product.quantity
    )

@app.get("/products", response_model=list[ProductResponse])
def list_products():
    products = list_products_controller()
    return [
        {
            "id": product[0],
            "product_code": product[1],
            "name": product[2],
            "price_unit": product[3],
            "quantity": product[4]
        }
        for product in products
    ]

@app.get("/products/{product_code}", response_model=ProductResponse)
def get_product(product_code: str):
    result = get_product_controller(product_code)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {
        "id": result[0],
        "product_code": result[1],
        "name": result[2],
        "price_unit": result[3],
        "quantity": result[4]
    }

@app.delete("/products/{product_code}", response_model=dict)
def delete_product(product_code: str):
    result = delete_product_controller(product_code)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result 