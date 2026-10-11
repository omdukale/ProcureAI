from database import get_connection, create_tables

def seed_database():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # VENDORS
    vendors = [
        ("V001", "SensorTech", 0.95, "Net 30"),
        ("V002", "Industrial Sensors Ltd", 0.88, "Net 15"),
        ("V003", "Precision Instruments", 0.97, "Net 30"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO vendors
        (vendor_id, name, reliability, payment_terms)
        VALUES (?, ?, ?, ?)
    """, vendors)

    # PRODUCTS
    products = [
        (
            "P001",
            "V001",
            "TempSensor-A",
            -20,
            150,
            0.5,
            800,
            20,
            3
        ),
        (
            "P002",
            "V002",
            "TempSensor-B",
            0,
            100,
            0.5,
            500,
            100,
            2
        ),
        (
            "P003",
            "V003",
            "TempSensor-C",
            -40,
            200,
            0.5,
            900,
            50,
            10
        ),
        (
            "P004",
            "V001",
            "TempSensor-D",
            -20,
            150,
            0.3,
            1100,
            50,
            4
        ),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO products
        (
            product_id,
            vendor_id,
            name,
            min_temp,
            max_temp,
            accuracy,
            price,
            stock,
            delivery_days
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products)

    # COMPANY POLICIES
    policies = [
        ("automatic_purchase_limit", "50000"),
        ("max_retries", "3"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO policies
        (policy_name, policy_value)
        VALUES (?, ?)
    """, policies)

    conn.commit()
    conn.close()
    print("Database seeded successfully.")


if __name__ == "__main__":
    seed_database()