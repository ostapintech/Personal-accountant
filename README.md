# Personal Accountant MVP

A lightweight, professional double-entry accounting application built with **Python**, **Streamlit**, and **SQLite**. This project demonstrates a clean separation of concerns, financial data integrity, and containerized deployment.

## 🚀 Quick Start

### Using Docker (Recommended)
Ensure you have Docker installed and running, then execute:

```bash
  docker build -t jito-accounting .
docker run -p 8501:8501 jito-accounting
```
The app will be available at `http://localhost:8501.`

Local Setup

Clone the repository.

Install dependencies:

```bash
  pip install -r requirements.txt
```

Run the application:

```bash
  streamlit run main.py
```
## 🖥️ How to Use

The application is divided into four main sections, accessible via the sidebar navigation:

### 1. Dashboard (Financial Overview)
- **Cash Balance:** Instantly see the current liquidity in the **1000 (Cash)** account.
- **Cash Trend Graph:** A dynamic line chart showing how your cash balance has changed over time. It calculates the cumulative sum of all cash-related transactions.

### 2. New Transaction (Data Entry)
This is where you record business events. The app automatically handles double-entry bookkeeping based on your selection:
- **Revenue:** Increases `1100 (Receivable)` and `4000 (Revenue)`. Use this when you provide a service but haven't received cash yet.
- **Client Payment:** Increases `1000 (Cash)` and decreases `1100 (Receivable)`. Use this when a client pays their debt.
- **Expense:** Increases `5000 (Expense)` and decreases `1000 (Cash)`.
- **Partner Linking:** You can link transactions to specific partners to track their individual balances.

### 3. P&L Report (Performance Tracking)
- **Date Filtering:** Select a custom date range to analyze performance.
- **Key Metrics:** View total Revenue, total Expenses, and Net Profit for the period.
- **Visual Analytics:** - A comparison chart for **Revenue vs. Expenses**.
    - A bar chart for **Daily Net Profit**.
    - A cumulative profit line to see business growth over time.

### 4. Partner Ledger (Debt Management)
- **Partner Management:** Add new clients directly within the interface.
- **Balance Tracking:** Select a partner to see their current **Receivable** status (how much they owe you).
- **Transaction History:** A detailed table of all historical operations associated with the selected partner for easy auditing.

---