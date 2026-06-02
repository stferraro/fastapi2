from inventario.models.product import create_product, delete_product, get_product_by_code, list_products


def add_product_controller(product_code, name, price_unit, quantity):
    if not product_code or not name:
        return {"error": "product_code and name are required"}

    if price_unit is None or quantity is None:
        return {"error": "price_unit and quantity are required"}

    create_product(product_code, name, price_unit, quantity)

    return {"message": "Product created successfully"}

def list_products_controller():
    products = list_products()

    return products

def get_product_controller(product_code):
    if not product_code:
        return {"error": "product_code is required"}
    
    product = get_product_by_code(product_code)
    
    if product is None:
        return {"error": "Product not found"}
    
    return product

def delete_product_controller(product_code):
    if not product_code:
        return {"error": "product_code is required"}
    
    product = get_product_by_code(product_code)
    
    if product is None:
        return {"error": "Product not found"}
    
    delete_product(product_code)

    return {"message": "Product deleted successfully"}