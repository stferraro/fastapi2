from ..database import connection

def create_product(product_code: str, name: str, price_unit: float, quantity: int):
    conn = connection.get_connection()

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (product_code, name, price_unit, quantity)
            VALUES (?, ?, ?, ?)
        """, (product_code, name, price_unit, quantity))

        conn.commit()
        conn.close()
        
def get_product_by_code(product_code: str):
    conn = connection.get_connection()

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, product_code, name, price_unit, quantity
            FROM products
            WHERE product_code = ?
        """, (product_code,))
        
        product = cursor.fetchone()
        conn.close()
        return product

    return None

def update_product_quantity(product_code: str, quantity: int):
    conn = connection.get_connection()

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products
            SET quantity = ?
            WHERE product_code = ?
        """, (quantity, product_code))

        conn.commit()
        conn.close()
        
def delete_product(product_code: str):
    conn = connection.get_connection()

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM products
            WHERE product_code = ?
        """, (product_code,))

        conn.commit()
        conn.close()
        
def list_products():
    
    conn = connection.get_connection()

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, product_code, name, price_unit, quantity
            FROM products
        """)
        
        products = cursor.fetchall()
        conn.close()
        return products

    return []