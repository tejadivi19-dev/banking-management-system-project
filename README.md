# 🏦 Banking System — Flask Web App

A full-stack banking web application built with **Flask** and **SQLite**.
Users can create an account, log in, deposit/withdraw money, transfer funds
to other accounts, view their transaction history, and change their PIN —
all through a browser.

This started as a console-based mini project and was rebuilt as a proper
web application as a web application with persistent database storage, 
password/PIN hashing, and a modular Flask structure.

## Features

- 🧾 **Account creation** — auto-generated 6-digit account number
- 🔐 **Secure login** — PINs are hashed with Werkzeug's `generate_password_hash`, never stored in plain text
- 💰 **Deposit / Withdraw** — with balance validation
- 🔁 **Transfer** — move money between any two accounts in the system
- 📜 **Transaction history** — every action is logged with a timestamp
- 🔑 **Change PIN** — with old-PIN verification
- 💾 **Persistent storage** — SQLite database via SQLAlchemy (data survives restarts, unlike an in-memory dictionary)

## Tech Stack

| Layer      | Technology            |
|------------|------------------------|
| Backend    | Python, Flask          |
| Database   | SQLite + Flask-SQLAlchemy |
| Frontend   | Jinja2 templates, Bootstrap 5 |
| Security   | Werkzeug password hashing, Flask sessions |

## Project Structure

```
banking-system/
├── app.py              # Flask app factory + all routes
├── config.py           # App configuration
├── extensions.py       # SQLAlchemy instance
├── models.py           # Account and Transaction database models
├── helpers.py          # Account number generation, auth decorator
├── requirements.txt
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── deposit.html
│   ├── withdraw.html
│   ├── transfer.html
│   ├── history.html
│   └── change_pin.html
└── static/
    └── style.css
```

## Setup & Run Locally

1. **Clone or download this folder**, then move into it:
   ```bash
   cd banking-webapp
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**:
   ```bash
   python app.py
   ```

5. Open your browser at **http://127.0.0.1:5000**

The SQLite database is created automatically when the application starts — no manual
database setup needed.

## How It Works

- Each account is a row in the `accounts` table with a hashed PIN.
- Every deposit, withdrawal, transfer, PIN change, and account creation
  writes a row to the `transactions` table, so the history page is a real
  audit trail rather than an in-memory list.
- Login state is kept in a Flask `session`, and the `@login_required`
  decorator protects every page that needs an authenticated user.

## Possible Next Steps

- Add email/OTP-based two-factor login
- Add account statements exportable as PDF/CSV
- Add interest calculation for savings accounts
- Deploy to Render/Railway/PythonAnywhere with a Postgres database
- Add unit tests with `pytest` and Flask's test client

## Why This Project

This project demonstrates:
- Building a multi-page web app with Flask's routing and templating
- Designing a relational schema (one-to-many: Account → Transactions)
- Implementing authentication and session management from scratch
- Following secure practices (no plaintext credentials)
- Structuring a Python project cleanly across multiple files instead of one script
