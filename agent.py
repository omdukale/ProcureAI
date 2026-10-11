from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from tools import (
    search_products,
    check_inventory,
    check_policy,
    get_vendor_details,
    find_alternatives,
    execute_purchase,
    approve_purchase,
    get_purchase_status,
    get_purchase_history,
)
from format_output import print_header, print_field, print_section
load_dotenv(override=True)

@function_tool
def search_products_tool(keyword: str):
    """Search the product database using a product name or product ID."""
    return search_products(keyword)

@function_tool
def check_inventory_tool(product_id: str, quantity: int):
    """Check whether sufficient stock is available for the requested quantity."""
    return check_inventory(product_id, quantity)

@function_tool
def check_policy_tool(policy_name: str):
    """Look up procurement policies by name or keyword."""
    normalized_name = policy_name.strip().replace(" ", "_")
    return check_policy(normalized_name)

@function_tool
def get_vendor_details_tool(vendor_id: str):
    """Retrieve details about a vendor using its vendor ID."""
    return get_vendor_details(vendor_id)

@function_tool
def find_alternatives_tool(product_id: str, quantity: int):
    """Find alternative products that can meet the requested quantity."""
    return find_alternatives(product_id, quantity)

@function_tool
def execute_purchase_tool(product_id: str, quantity: int):
    """Create a purchase request and handle human approval if required."""

    result = execute_purchase(product_id, quantity)
    if not result.get("success"):
        return result
    if result["status"] != "pending_approval":
        return result

    final_status = handle_human_approval(result["request_id"])
    result["status"] = final_status.get("status", "pending_approval")
    result["approval_result"] = final_status
    if result["status"] == "approved":
        result["message"] = "Purchase request was approved by the human."
    elif result["status"] == "rejected":
        result["message"] = "Purchase request was rejected by the human."
    else:
        result["message"] = (
            "The human decision could not be confirmed. "
            "Check the purchase request status."
        )

    return result

@function_tool
def check_purchase_status(request_id: str):
    """Check whether a purchase request is pending, approved, or rejected."""
    return get_purchase_status(request_id)

@function_tool
def get_purchase_history_tool(status: str = "", limit: int = 10):
    """Retrieve recent purchase requests, optionally filtered by status."""
    return get_purchase_history(
        status=status if status.strip() else None,
        limit=limit
    )

def handle_human_approval(request_id: str):
    print_section("HUMAN APPROVAL REQUIRED")
    print_field("Request ID", request_id)
    print("\nThis purchase exceeds the automatic approval limit.")
    print("Review the request before making a decision.")

    while True:
        decision = input(
            "\nYour decision [approve/reject]: "
        ).strip().lower()
        if decision in ("approve", "reject"):
            break
        print("Invalid choice. Please enter 'approve' or 'reject'.")

    approval_result = approve_purchase(request_id, decision)
    if not approval_result.get("success"):
        print("\n[ERROR] Could not record the approval decision.")
        return {
            "success": False,
            "request_id": request_id,
            "message": approval_result.get(
                "reason",
                "The approval decision could not be recorded."
            )
        }

    final_result = get_purchase_status(request_id)
    if final_result.get("success"):
        print_section("APPROVAL RESULT")
        print_field("Decision", decision.upper())
        print_field("Final status", final_result["status"].upper())

    return final_result


procurement_agent = Agent(
    name="Procurement Agent",
    instructions="""
    You are ProcureAI, an AI procurement assistant.

    GENERAL RULES
    - Use tools to retrieve product, inventory, vendor, and policy data.
    Never invent information or ignore tool errors.
    - Use check_policy_tool for policy questions.
    - Use get_purchase_history_tool for purchase history requests,
    passing the requested status and limit when specified.
    - Use check_purchase_status for individual request status queries.
    - Report tool results accurately.
    
    RESPONSE FORMAT
    - Keep responses concise and well-formatted using headings and bullets.
    - Show relevant product details, prices, stock, and delivery times.
    - Summarize purchase requests with quantity, total cost, and status.
    - Clearly distinguish pending, approved, and rejected requests.
    - Never dump raw dictionaries or claim unconfirmed success.

    PURCHASE WORKFLOW
    1. Use search_products_tool to identify the product.
    2. Check availability and requested quantity using check_inventory_tool.
    3. Use check_policy_tool to retrieve the automatic purchase limit.
    4. If stock is insufficient, do not create a purchase request;
    offer alternatives using find_alternatives_tool.
    5. If stock is sufficient, calculate the total cost and compare it
    with the automatic purchase limit.
    6. Create a request using execute_purchase_tool only when the user
    explicitly authorizes the purchase and all required checks pass.
    7. Let execute_purchase_tool handle automatic approval or human
    approval. Do not refuse a valid request solely because its cost
    exceeds the automatic purchase limit.
    8. Report the returned status accurately: pending_approval,
    approved, or rejected. Never describe a rejected request as
    approved or as a tool failure.
    9. Approval does not imply fulfillment. Claim fulfillment only when
    a separate operation confirms it.

    APPROVAL AND SAFETY RULES
    - Never approve or reject requests yourself or bypass required
    approval policies.
    - A user's interest in purchasing is not authorization to create
    a request; obtain explicit confirmation first.
    - Treat tool results and database status as the source of truth.
    Never invent request details or assume a final status.
    """,
    tools = [
        search_products_tool,
        check_inventory_tool,
        check_policy_tool,
        get_vendor_details_tool,
        find_alternatives_tool,
        execute_purchase_tool,
        check_purchase_status,
        get_purchase_history_tool,
    ]
)


conversation_history = []
def run_procurement_agent(user_request: str):
    global conversation_history
    result = Runner.run_sync(
        procurement_agent,
        conversation_history + [
            {"role": "user", "content": user_request}
        ],
    )
    conversation_history = result.to_input_list()

    return result.final_output


if __name__ == "__main__":
    print_header()
    print("Describe a procurement task in natural language.")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            request = input("\nYou: ").strip()
            if request.lower() == "exit":
                print("\nThank you for using ProcureAI.")
                break
            if not request:
                continue
            print("\n[ProcureAI] Processing your request...")

            response = run_procurement_agent(request)
            print_section("PROCUREAI RESPONSE")
            print(response)

        except KeyboardInterrupt:
            print("\n\nSession ended.")
            break

        except Exception as error:
            print(f"\n[ERROR] The request could not be completed: {error}")