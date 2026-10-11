
from tools import get_pending_requests

requests = get_pending_requests()

if not requests:
    print("No purchase requests are awaiting approval.")
else:
    for request in requests:
        print(request)
