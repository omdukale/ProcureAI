from database import get_connection

conn = get_connection()
cursor = conn.cursor()

print("\nPRODUCTS")
print("-" * 50)

cursor.execute("SELECT * FROM products")

for product in cursor.fetchall():
    print(dict(product))

print("\nVENDORS")
print("-" * 50)

cursor.execute("SELECT * FROM vendors")

for vendor in cursor.fetchall():
    print(dict(vendor))

print("\nPOLICIES")
print("-" * 50)

cursor.execute("SELECT * FROM policies")

for policy in cursor.fetchall():
    print(dict(policy))

conn.close()