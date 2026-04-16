import streamlit as st
from logic.reports import ReportService
from db import get_connection

st.sidebar.title("Навігація")
page = st.sidebar.radio("Оберіть сторінку", ["Транзакції", "P&L Звіт", "Партнери"])

if page == "Партнери":
    st.header("Книга партнерів")

    # Отримуємо список партнерів для випадаючого списку
    with get_connection() as conn:
        partners = conn.execute("SELECT id, name FROM partners").fetchall()

    partner_options = {p["name"]: p["id"] for p in partners}
    selected_name = st.selectbox("Оберіть партнера", list(partner_options.keys()))

    if selected_name:
        p_id = partner_options[selected_name]
        ledger = ReportService.get_partner_ledger(p_id)

        col1, col2 = st.columns(2)
        col1.metric("Він винен нам (AR)", f"{ledger.receivable} $")
        col2.metric("Ми винні йому (AP)", f"{ledger.payable} $")