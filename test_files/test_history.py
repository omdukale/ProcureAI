
from tools import get_purchase_history

# Retrieve the 10 most recent requests
print(get_purchase_history())

# Retrieve only rejected requests
print(get_purchase_history(status="rejected"))

# Test invalid status handling
print(get_purchase_history(status="cancelled"))
