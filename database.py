import sqlite3
from contextlib import contextmanager

DB = "shop.db"

@contextmanager
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            photo_url TEXT,
            stock INTEGER DEFAULT 0
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

def get_products():
    with db() as c:
        return c.execute("SELECT * FROM products ORDER BY id DESC").fetchall()

def get_product(pid):
    with db() as c:
        return c.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()

def add_product(name, desc, price, photo, stock):
    with db() as c:
        c.execute(
            "INSERT INTO products (name,description,price,photo_url,stock) VALUES (?,?,?,?,?)",
            (name, desc, price, photo, stock)
        )

def update_product(pid, name, desc, price, photo, stock):
    with db() as c:
        c.execute(
            "UPDATE products SET name=?, description=?, price=?, photo_url=?, stock=? WHERE id=?",
            (name, desc, price, photo, stock, pid)
        )

def delete_product(pid):
    with db() as c:
        c.execute("DELETE FROM products WHERE id=?", (pid,))

def add_order(user_id, username, product_id):
    with db() as c:
        c.execute(
            "INSERT INTO orders (user_id, username, product_id) VALUES (?,?,?)",
            (user_id, username, product_id)
        )
