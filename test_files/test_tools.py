
from tools import search_products, check_inventory, check_policy

print("=== PRODUCT SEARCH ===")
products = search_products("")

for product in products:
    print(product)

print("\n=== INVENTORY CHECK ===")

if products:
    product_id = products[0]["product_id"]
    print(check_inventory(product_id, 5))
else:
    print("No products found. Check seed.py.")

print("\n=== POLICY CHECK ===")
print(check_policy(""))
    