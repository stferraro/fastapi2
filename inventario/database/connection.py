import sqlite3
import os


def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "inventario.db")
    try:
        connection = sqlite3.connect(db_path)
        return connection

    except sqlite3.Error as e:
        print(f"Error to connect to the database: {e}")
        return None


def create_tables():
    connection = get_connection()

    if connection is not None:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                price_unit REAL NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)

        connection.commit()
        connection.close()