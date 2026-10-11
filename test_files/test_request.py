
from database import get_connection

conn = get_connection()

try:
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT request_id, product_id, quantity, total_cost, status
        FROM purchase_requests
        ORDER BY created_at DESC
        """
    )

    requests = cursor.fetchall()

    if requests is None:
        print("Purchase request not found.")
    else:
        for request in requests:
            print(dict(request))

finally:
    conn.close()
