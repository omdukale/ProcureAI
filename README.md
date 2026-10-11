# ProcureAI — AI-Powered Procurement Assistant

ProcureAI is an AI-powered procurement assistant built using Python, the OpenAI Agents SDK, and SQLite. It automates key steps in a procurement workflow through natural-language interactions.

## Features

- **Product Discovery:** Search for products using natural-language requests.
- **Inventory Management:** Check stock availability before purchasing.
- **Alternative Recommendations:** Find alternative products when requested quantities exceed available stock.
- **Policy Validation:** Check procurement policies and spending limits.
- **Human-in-the-Loop Approval:** Route purchases requiring approval to a human for approval or rejection.
- **Purchase Tracking:** Retrieve purchase statuses and purchase history.
- **Database Integration:** Store product, vendor, inventory, and purchase information in SQLite.

## Tech Stack

- Python
- OpenAI Agents SDK
- SQLite
- python-dotenv
- uv

## Setup

1. Clone this repository.
2. Install Python 3.12 or later.
3. Install the dependencies listed in `pyproject.toml`.
4. Create a `.env` file and add your OpenAI API key:

   `OPENAI_API_KEY=your_api_key_here`

5. Initialize the database and populate the sample data using the project's setup scripts.
6. Run the application using the configured Python environment.

## Notes

This is a prototype demonstrating an AI-assisted procurement workflow. It uses sample data and does not make real purchases or integrate with live vendors or payment systems.