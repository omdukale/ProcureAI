def print_header():
    print("\nPROCUREAI")
    print("Intelligent Procurement Assistant\n")

def print_section(title):
    print(f"\n{title} : " )

def print_field(label, value):
    print(f"{label:<20}: {value}")

def format_currency(amount):
    return f"${amount:,.2f}"
