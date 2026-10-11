import sqlite3
DB_PATH = "data/company.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # vendors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            reliability REAL NOT NULL,
            payment_terms TEXT NOT NULL
        )
    """)

    # products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            vendor_id TEXT NOT NULL,
            name TEXT NOT NULL,
            min_temp REAL NOT NULL,
            max_temp REAL NOT NULL,
            accuracy REAL NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            delivery_days INTEGER NOT NULL,
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
        )
    """)

    # company procurement policies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_name TEXT PRIMARY KEY,
            policy_value TEXT NOT NULL
        )
    """)

    # purchase requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_requests (
            request_id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")

