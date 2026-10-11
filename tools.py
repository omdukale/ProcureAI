from database import get_connection


def search_products(keyword: str):
    """Search for products by name or product ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT product_id, vendor_id, name, min_temp, max_temp,
               accuracy, price, stock, delivery_days
        FROM products
        WHERE name LIKE ? OR product_id LIKE ?
        """,
        (f"%{keyword}%", f"%{keyword}%")
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "product_id": row["product_id"],
            "vendor_id": row["vendor_id"],
            "name": row["name"],
            "min_temp": row["min_temp"],
            "max_temp": row["max_temp"],
            "accuracy": row["accuracy"],
            "price": row["price"],
            "stock": row["stock"],
            "delivery_days": row["delivery_days"]
        }
        for row in rows
    ]


def check_inventory(product_id: str, quantity: int):
    """Check whether sufficient stock is available."""
    if quantity <= 0:
        return {
            "success": False,
            "reason": "Quantity must be greater than zero."
        }

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, stock FROM products WHERE product_id = ?",
        (product_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {
            "success": False,
            "reason": f"Product '{product_id}' was not found."
        }

    return {
        "success": True,
        "product_id": product_id,
        "product_name": row["name"],
        "requested_quantity": quantity,
        "available_stock": row["stock"],
        "sufficient_stock": row["stock"] >= quantity
    }


def check_policy(policy_name: str):
    """Retrieve company policies by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT policy_name, policy_value
        FROM policies
        WHERE policy_name LIKE ?
        """,
        (f"%{policy_name}%",)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "policy_name": row["policy_name"],
            "policy_value": row["policy_value"]
        }
        for row in rows
    ]


def get_vendor_details(vendor_id: str):
    """Retrieve information about a vendor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT vendor_id, name, reliability, payment_terms
        FROM vendors
        WHERE vendor_id = ?
        """,
        (vendor_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return {
            "success": False,
            "reason": f"Vendor '{vendor_id}' was not found."
        }

    return {
        "success": True,
        "vendor_id": row["vendor_id"],
        "name": row["name"],
        "reliability": row["reliability"],
        "payment_terms": row["payment_terms"]
    }


def execute_purchase(product_id: str, quantity: int):
    """Validate a purchase and record it or queue it for approval."""
    import uuid
    from datetime import datetime, timezone

    if quantity <= 0:
        return {
            "success": False,
            "reason": "Quantity must be greater than zero."
        }

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT name, price, stock
            FROM products
            WHERE product_id = ?
            """,
            (product_id,)
        )
        product = cursor.fetchone()
        if product is None:
            return {
                "success": False,
                "reason": f"Product '{product_id}' was not found."
            }
        if product["stock"] < quantity:
            return {
                "success": False,
                "reason": "Insufficient inventory.",
                "available_stock": product["stock"],
                "requested_quantity": quantity
            }

        cursor.execute(
            """
            SELECT policy_value
            FROM policies
            WHERE policy_name = 'automatic_purchase_limit'
            """
        )
        policy = cursor.fetchone()
        if policy is None:
            return {
                "success": False,
                "reason": "Automatic purchase limit is not configured."
            }

        total_cost = product["price"] * quantity
        purchase_limit = float(policy["policy_value"])

        if total_cost > purchase_limit:
            status = "pending_approval"
        else:
            status = "approved"

        request_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO purchase_requests
            (request_id, product_id, quantity, total_cost, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                product_id,
                quantity,
                total_cost,
                status,
                datetime.now(timezone.utc).isoformat()
            )
        )
        conn.commit()

        return {
            "success": True,
            "request_id": request_id,
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "total_cost": total_cost,
            "status": status,
            "message": (
                "Purchase request created and is waiting for human approval."
                if status == "pending_approval"
                else "Purchase request created and passed the automatic limit check."
            )
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def find_alternatives(product_id: str, quantity: int):
    """Find in-stock alternatives that satisfy the original specifications."""

    if quantity <= 0:
        return {
            "success": False,
            "reason": "Quantity must be greater than zero."
        }
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT product_id, name, min_temp, max_temp, accuracy
            FROM products
            WHERE product_id = ?
            """,
            (product_id,)
        )
        original = cursor.fetchone()
        if original is None:
            return {
                "success": False,
                "reason": f"Product '{product_id}' was not found."
            }

        cursor.execute(
            """
            SELECT product_id, vendor_id, name, min_temp, max_temp,
                   accuracy, price, stock, delivery_days
            FROM products
            WHERE product_id != ?
              AND stock >= ?
            """,
            (product_id, quantity)
        )
        candidates = cursor.fetchall()
        alternatives = []
        for candidate in candidates:
            meets_temperature = (
                candidate["min_temp"] <= original["min_temp"]
                and candidate["max_temp"] >= original["max_temp"]
            )
            meets_accuracy = (
                candidate["accuracy"] <= original["accuracy"]
            )
            if meets_temperature and meets_accuracy:
                alternatives.append({
                    "product_id": candidate["product_id"],
                    "vendor_id": candidate["vendor_id"],
                    "name": candidate["name"],
                    "price": candidate["price"],
                    "stock": candidate["stock"],
                    "delivery_days": candidate["delivery_days"],
                    "min_temp": candidate["min_temp"],
                    "max_temp": candidate["max_temp"],
                    "accuracy": candidate["accuracy"],
                    "total_cost": candidate["price"] * quantity
                })

        alternatives.sort(
            key=lambda item: (
                item["total_cost"],
                item["delivery_days"]
            )
        )

        return {
            "success": True,
            "original_product": original["name"],
            "requested_quantity": quantity,
            "alternatives": alternatives
        }

    finally:
        conn.close()


def approve_purchase(request_id: str, decision: str):
    """Approve or reject a purchase request awaiting human review."""

    decision = decision.strip().lower()
    if decision not in ("approve", "reject"):
        return {
            "success": False,
            "reason": "Decision must be 'approve' or 'reject'."
        }
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT request_id, product_id, quantity, total_cost, status
            FROM purchase_requests
            WHERE request_id = ?
            """,
            (request_id,)
        )
        request = cursor.fetchone()
        if request is None:
            return {
                "success": False,
                "reason": "Purchase request not found."
            }
        if request["status"] != "pending_approval":
            return {
                "success": False,
                "reason": (
                    f"Request cannot be reviewed because its status is "
                    f"'{request['status']}'."
                )
            }
        new_status = (
            "approved" if decision == "approve" else "rejected"
        )

        cursor.execute(
            """
            UPDATE purchase_requests
            SET status = ?
            WHERE request_id = ? AND status = 'pending_approval'
            """,
            (new_status, request_id)
        )
        if cursor.rowcount != 1:
            conn.rollback()
            return {
                "success": False,
                "reason": "Request status changed before the decision was saved."
            }
        conn.commit()

        return {
            "success": True,
            "request_id": request_id,
            "product_id": request["product_id"],
            "total_cost": request["total_cost"],
            "status": new_status,
            "message": f"Purchase request {new_status}."
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_pending_requests():
    """Return all purchase requests awaiting human approval."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                request_id,
                product_id,
                quantity,
                total_cost,
                status,
                created_at
            FROM purchase_requests
            WHERE status = 'pending_approval'
            ORDER BY created_at ASC
            """
        )
        rows = cursor.fetchall()

        return [
            {
                "request_id": row["request_id"],
                "product_id": row["product_id"],
                "quantity": row["quantity"],
                "total_cost": row["total_cost"],
                "status": row["status"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

    finally:
        conn.close()



def get_purchase_status(request_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT request_id, status
            FROM purchase_requests
            WHERE request_id = ?
            """,
            (request_id,)
        )
        request = cursor.fetchone()
        if request is None:
            return {
                "success": False,
                "message": "Purchase request not found."
            }

        return {
            "success": True,
            "request_id": request["request_id"],
            "status": request["status"]
        }

    finally:
        cursor.close()
        conn.close()


def get_purchase_history(status: str = None, limit: int = 10):
    """Retrieve recent purchase requests, optionally filtered by status."""

    valid_statuses = (
        "pending_approval",
        "approved",
        "rejected"
    )
    if status is not None:
        status = status.strip().lower()
        if status not in valid_statuses:
            return {
                "success": False,
                "message": (
                    "Invalid status. Use pending_approval, "
                    "approved, or rejected."
                )
            }

    if limit <= 0:
        return {
            "success": False,
            "message": "Limit must be greater than zero."
        }
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if status is None:
            cursor.execute(
                """
                SELECT request_id, product_id, quantity,
                       total_cost, status, created_at
                FROM purchase_requests
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,)
            )
        else:
            cursor.execute(
                """
                SELECT request_id, product_id, quantity,
                       total_cost, status, created_at
                FROM purchase_requests
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (status, limit)
            )
        requests = [dict(row) for row in cursor.fetchall()]

        return {
            "success": True,
            "count": len(requests),
            "requests": requests
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

    finally:
        conn.close()
