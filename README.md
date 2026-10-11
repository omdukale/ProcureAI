# ProcureAI — AI-Powered Procurement Assistant

ProcureAI is an AI-powered procurement assistant built using Python, the OpenAI Agents SDK, and SQLite. It automates key steps in a procurement workflow through natural-language interactions.

## Features

- Natural-language product search
- Inventory availability checking
- Alternative product recommendations when stock is insufficient
- Procurement policy validation
- Automatic approval for purchases within configured limits
- Human-in-the-loop approval for high-value purchases
- Purchase status and history tracking
- SQLite-based data persistence

## Architecture

ProcureAI uses an AI agent built with the OpenAI Agents SDK to interpret user requests and decide which tools to invoke.

The agent interacts with Python function tools responsible for product search, inventory checks, policy validation, alternative discovery, and purchase management. These tools connect to a SQLite database containing product, vendor, policy, and purchase request data.

Business-critical decisions such as inventory validation and approval limits are handled deterministically through Python logic. Purchases exceeding the configured limit require human approval before the final status is recorded.

## Design Decisions

- **Agent-based orchestration:** The AI agent handles natural-language understanding and tool selection.
- **Tool-based execution:** Database operations and business rules are handled through Python tools for reliability.
- **Human oversight:** High-value purchases require approval to prevent unauthorized actions.
- **Database-backed workflow:** SQLite stores procurement data and maintains purchase history.

## Setup

Clone the repository:

```bash
git clone https://github.com/omdukale/ProcureAI.git
cd ProcureAI
```

Install dependencies:

```bash
uv sync
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

Initialize the database:

```bash
python seed.py
```

Run the application:

```bash
python agent.py
```

## Notes

This is a prototype demonstrating an AI-assisted procurement workflow. It uses sample data and does not make real purchases or integrate with live vendors or payment systems.
