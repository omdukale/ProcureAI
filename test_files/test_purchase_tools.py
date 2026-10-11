
from tools import get_vendor_details, execute_purchase
print(execute_purchase("P004", 30))

from database import get_connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT request_id, product_id, quantity, total_cost, status
    FROM purchase_requests
    ORDER BY created_at DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(dict(row))
conn.close()