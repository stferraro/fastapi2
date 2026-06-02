from pydantic import BaseModel


class ProductCreate(BaseModel):
    product_code: str
    name: str
    price_unit: float
    quantity: int
    
    
class ProductResponse(BaseModel):
    id: int
    product_code: str
    name: str
    price_unit: float
    quantity: int
    