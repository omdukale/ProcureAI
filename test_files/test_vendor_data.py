
from database import get_connection

conn = get_connection()
cursor = conn.cursor()

for table in ["vendors", "purchase_requests"]:
    print(f"\n=== {table.upper()} DATA ===")
    cursor.execute(f"SELECT * FROM {table}")

    columns = [item[0] for item in cursor.description]

    for row in cursor.fetchall():
        print(dict(zip(columns, row)))

conn.close()
