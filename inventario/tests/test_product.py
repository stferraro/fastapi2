from fastapi.testclient import TestClient
from inventario.main import app

client = TestClient(app)

def test_create_product():
    response = client.post("/products", json={
        "product_code": "P001",
        "name": "Producto Test",
        "price_unit": 10.5,
        "quantity": 5
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Product created successfully"
    
def test_get_product():
    # First, create a product to ensure it exists
    client.post("/products", json={
        "product_code": "P002",
        "name": "Producto Test 2",
        "price_unit": 15.0,
        "quantity": 3
    })
    
    response = client.get("/products/P002")
    assert response.status_code == 200
    product = response.json()
    assert product["product_code"] == "P002"
    assert product["name"] == "Producto Test 2"
    assert product["price_unit"] == 15.0
    assert product["quantity"] == 3
    
def test_delete_product():
    # First, create a product to ensure it exists
    client.post("/products", json={
        "product_code": "P003",
        "name": "Producto Test 3",
        "price_unit": 20.0,
        "quantity": 2
    })
    
    response = client.delete("/products/P003")
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"
    
    # Verify the product is deleted
    response = client.get("/products/P003")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
    
def test_list_products():
    # Create multiple products
    client.post("/products", json={
        "product_code": "P004",
        "name": "Producto Test 4",
        "price_unit": 25.0,
        "quantity": 1
    })
    client.post("/products", json={
        "product_code": "P005",
        "name": "Producto Test 5",
        "price_unit": 30.0,
        "quantity": 4
    })
    
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert any(p["product_code"] == "P004" for p in products)
    assert any(p["product_code"] == "P005" for p in products)
    
def test_update_product_quantity():
    # First, create a product to ensure it exists
    client.post("/products", json={
        "product_code": "P006",
        "name": "Producto Test 6",
        "price_unit": 35.0,
        "quantity": 10
    })
    
    # Update the product quantity
    response = client.put("/products/P006/quantity", json={"quantity": 15})
    assert response.status_code == 200
    assert response.json()["message"] == "Product quantity updated successfully"
    
    # Verify the quantity is updated
    response = client.get("/products/P006")
    assert response.status_code == 200
    product = response.json()
    assert product["quantity"] == 15
    
