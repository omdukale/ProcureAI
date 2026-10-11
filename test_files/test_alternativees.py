
from tools import check_inventory, find_alternatives

product_id = "P004"
quantity = 100

print("=== ORIGINAL REQUEST ===")
print(check_inventory(product_id, quantity))

print("\n=== ALTERNATIVE PRODUCTS ===")
result = find_alternatives(product_id, quantity)
print(result)

if result["success"] and result["alternatives"]:
    print("\n=== ALTERNATIVES SUMMARY ===")

    for product in result["alternatives"]:
        print(
            f'{product["product_id"]}: {product["name"]} | '
            f'Total: ₹{product["total_cost"]} | '
            f'Stock: {product["stock"]} | '
            f'Delivery: {product["delivery_days"]} days'
        )
