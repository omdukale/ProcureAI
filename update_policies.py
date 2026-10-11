from database import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute(
    """
    UPDATE policies
    SET policy_value = ?
    WHERE policy_name = ?
    """,
    (30000, "automatic_purchase_limit")
)
conn.commit()
conn.close()

if cursor.rowcount == 0:
    print("Policy not found. No changes made.")
else:
    conn.commit()
    print("Automatic purchase limit updated to 30000.")

