import streamlit as st
import pandas as pd
from datetime import date
from db import init_db, get_connection
from logic.transactions import Transaction
from logic.partner_ledger import PartnerLedger
from logic.profit_loss import ProfitLoss

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Personal Accountant",
    layout="wide",
    page_icon="💼"
)

# --- CUSTOM STYLE (light green accent) ---
st.markdown("""
<style>
/* Background */
.stApp {
    background-color: #f6fff8;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #eafff1;
}

/* Buttons */
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.5em 1em;
}
.stButton>button:hover {
    background-color: #43a047;
}

/* Metrics */
[data-testid="metric-container"] {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #d0f0d8;
}

/* Inputs */
input, textarea {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# --- INIT DB ---
init_db()

# --- SIDEBAR ---
st.sidebar.title("💼 Accountant")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "New Transaction", "P&L Report", "Partner Ledger"]
)

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":
    st.title("📊 Financial Overview")

    with get_connection() as conn:
        cash = conn.execute(
            "SELECT SUM(debit - credit) as bal FROM entries WHERE account_id = 1000"
        ).fetchone()['bal'] or 0.0

    col1, col2 = st.columns(2)

    col1.metric("Cash Balance (1000)", f"{cash:.2f} $")
    col2.info("Welcome! Use the sidebar to manage transactions and reports.")

    # --- CASH TREND ---
    with get_connection() as conn:
        cash_rows = conn.execute(
            """
            SELECT
                t.date AS date,
                SUM(e.debit - e.credit) AS daily_delta
            FROM transactions t
            JOIN entries e ON e.transaction_id = t.id
            WHERE e.account_id = 1000
            GROUP BY t.date
            ORDER BY t.date
            """
        ).fetchall()

    if cash_rows:
        cash_df = pd.DataFrame(
            [{"date": r["date"], "daily_delta": r["daily_delta"] or 0.0} for r in cash_rows]
        )
        cash_df["date"] = pd.to_datetime(cash_df["date"])
        cash_df["cash_balance"] = cash_df["daily_delta"].cumsum()

        st.subheader("Cash Balance Over Time")
        st.line_chart(
            cash_df.set_index("date")[["cash_balance"]],
            use_container_width=True
        )
    else:
        st.info("Add a transaction to see cash trend on the dashboard.")

# =========================
# NEW TRANSACTION
# =========================
elif page == "New Transaction":
    st.title("📝 Create Transaction")

    # Load partners to link transactions to Partner Ledger balances.
    with get_connection() as conn:
        partners_rows = conn.execute(
            "SELECT id, name, type FROM partners ORDER BY name"
        ).fetchall()

    client_options = {
        p["name"]: p["id"] for p in partners_rows if p["type"] == "Client"
    }

    with st.form("tx_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        desc = col1.text_input(
            "Description",
            placeholder="e.g. Service sale"
        )

        tx_date = col1.date_input(
            "Transaction date",
            value=date.today(),
        )

        amount = col2.number_input(
            "Amount ($)",
            min_value=0.01,
            step=0.01
        )

        tx_type = st.selectbox(
            "Transaction Type",
            [
                "Revenue (Client owes us)",
                "Client Payment (Cash)",
                "Expense (Cash payment)"
            ]
        )

        partner_id = None
        if tx_type in {"Revenue (Client owes us)", "Client Payment (Cash)"}:
            # Allow creating a transaction without linking to a partner.
            # "None" will set `partner_id=None` (so Partner Ledger won't show it).
            client_select_options: list[str] = ["None"]
            if client_options:
                client_select_options.extend(list(client_options.keys()))

            selected_client_name = st.selectbox(
                "Partner (Client)",
                client_select_options,
                key="partner_client_select",
                index=(1 if len(client_select_options) > 1 else 0),
            )

            if selected_client_name != "None":
                partner_id = client_options[selected_client_name]

        submitted = st.form_submit_button("Save Transaction")

        if submitted:
            if tx_date > date.today():
                st.error("Transaction date cannot be in the future.")
            else:
                try:
                    new_tx = Transaction(
                        date=str(tx_date),
                        description=desc,
                        partner_id=partner_id,
                    )

                    if tx_type == "Revenue (Client owes us)":
                        new_tx.add_entry(account_id=1100, debit=amount)
                        new_tx.add_entry(account_id=4000, credit=amount)

                    elif tx_type == "Client Payment (Cash)":
                        new_tx.add_entry(account_id=1000, debit=amount)
                        new_tx.add_entry(account_id=1100, credit=amount)

                    elif tx_type == "Expense (Cash payment)":
                        new_tx.add_entry(account_id=5000, debit=amount)
                        new_tx.add_entry(account_id=1000, credit=amount)

                    new_tx.save()
                    st.success("✅ Transaction saved successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# =========================
# P&L REPORT
# =========================
elif page == "P&L Report":
    st.title("📈 Profit & Loss")

    col1, col2 = st.columns(2)
    start = col1.date_input("From", value=date(2026, 1, 1))
    end = col2.date_input("To", value=date.today())

    report = ProfitLoss.get_profit_and_loss(str(start), str(end))

    c1, c2, c3 = st.columns(3)

    c1.metric("Revenue (4000)", f"{report.revenue:.2f} $")
    c2.metric("Expenses (5000)", f"{report.expenses:.2f} $")
    c3.metric("Net Profit", f"{report.net_profit:.2f} $")

    # --- P&L CHARTS (date range aware) ---
    with get_connection() as conn:
        pl_rows = conn.execute(
            """
            SELECT
                t.date AS date,
                SUM(CASE WHEN e.account_id = 4000 THEN (e.credit - e.debit) ELSE 0 END) AS revenue,
                SUM(CASE WHEN e.account_id = 5000 THEN (e.debit - e.credit) ELSE 0 END) AS expenses
            FROM transactions t
            JOIN entries e ON e.transaction_id = t.id
            WHERE t.date BETWEEN ? AND ?
              AND e.account_id IN (4000, 5000)
            GROUP BY t.date
            ORDER BY t.date
            """,
            (str(start), str(end)),
        ).fetchall()

    if pl_rows:
        pl_df = pd.DataFrame(
            [{"date": r["date"], "revenue": r["revenue"] or 0.0, "expenses": r["expenses"] or 0.0} for r in pl_rows]
        )
        pl_df["date"] = pd.to_datetime(pl_df["date"])
        pl_df["net_profit"] = pl_df["revenue"] - pl_df["expenses"]

        st.subheader("Revenue / Expenses by Date")
        st.line_chart(
            pl_df.set_index("date")[["revenue", "expenses", "net_profit"]],
            use_container_width=True
        )

        pl_df["cumulative_net_profit"] = pl_df["net_profit"].cumsum()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Net Profit (Bar)")
            st.bar_chart(
                pl_df.set_index("date")[["net_profit"]],
                use_container_width=True
            )
        with c2:
            st.subheader("Cumulative Net Profit")
            st.line_chart(
                pl_df.set_index("date")[["cumulative_net_profit"]],
                use_container_width=True
            )
    else:
        st.info("No P&L data in the selected date range.")

# =========================
# PARTNER LEDGER
# =========================
elif page == "Partner Ledger":
    st.title("👥 Partner Ledger")

    # --- ADD NEW PARTNER ---
    with st.expander("➕ Add New Partner"):
        with st.form("add_partner_form"):
            col1, col2 = st.columns(2)

            p_name = col1.text_input("Partner Name")
            # Suppliers are disabled; only clients are supported.
            p_type = "Client"

            submitted = st.form_submit_button("Create Partner")

            if submitted:
                if p_name.strip():
                    with get_connection() as conn:
                        conn.execute(
                            "INSERT INTO partners (name, type) VALUES (?, ?)",
                            (p_name, p_type)
                        )
                    st.success(f"✅ Partner '{p_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a name")

    st.divider()

    # --- LOAD PARTNERS ---
    with get_connection() as conn:
        partners_rows = conn.execute(
            "SELECT id, name FROM partners WHERE type = 'Client' ORDER BY name"
        ).fetchall()

    if not partners_rows:
        st.info("No partners yet. Add one above.")
    else:
        partner_options = {p["name"]: p["id"] for p in partners_rows}

        selected_name = st.selectbox(
            "Select Partner",
            list(partner_options.keys())
        )

        if selected_name:
            p_id = partner_options[selected_name]

            # --- SERVICE CALL ---
            ledger = PartnerLedger.get_partner_ledger(p_id)

            # --- METRICS ---
            c1, c2 = st.columns(2)

            c1.metric(
                "Receivable (1100)",
                f"{ledger.receivable:.2f} $"
            )
            balance_color = "normal" if ledger.net_balance >= 0 else "inverse"
            c2.metric(
                "Net Balance",
                f"{ledger.net_balance:.2f} $",
                delta_color=balance_color
            )

            st.divider()

            # --- TRANSACTION HISTORY ---
            st.subheader(f"📜 Transaction History: {selected_name}")

            if ledger.transactions:
                st.dataframe(
                    ledger.transactions,
                    use_container_width=True
                )
            else:
                st.info("No transactions for this partner yet.")