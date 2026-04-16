from db import get_connection
from dataclasses import dataclass, field

from typing import Any

@dataclass
class PartnerBalance:
    partner_name: str
    receivable: float
    payable: float
    net_balance: float
    # Used directly by `st.dataframe()` in `main.py`
    transactions: list[dict[str, Any]] = field(default_factory=list)

class PartnerLedger:
    @staticmethod
    def get_partner_ledger(partner_id: int) -> PartnerBalance:
        """
        Shows the status with a specific partner.
        """
        query = """
                SELECT 
                    p.name as partner_name,
                    e.account_id,
                    SUM(e.debit - e.credit) as balance
                FROM partners p
                JOIN transactions t ON p.id = t.partner_id
                JOIN entries e ON t.id = e.transaction_id
                WHERE p.id = ? AND e.account_id IN (1100, 2000)
                GROUP BY e.account_id
            """

        receivable = 0.0
        payable = 0.0
        partner_name = "Unknown"

        with get_connection() as conn:
            rows = conn.execute(query, (partner_id,)).fetchall()

            for row in rows:
                partner_name = row["partner_name"]
                acc_id = row["account_id"]
                bal = row["balance"] or 0.0

                if acc_id == 1100:
                    receivable = bal
                elif acc_id == 2000:
                    #positive debt
                    payable = -bal

            # --- Transaction history (for UI) ---
            # We only show movements that affect receivable/payable accounts.
            history_query = """
                SELECT
                    p.name AS partner_name,
                    t.id AS transaction_id,
                    t.date AS date,
                    t.description AS description,
                    SUM(CASE WHEN e.account_id = 1100 THEN (e.debit - e.credit) ELSE 0 END) AS receivable_change,
                    -SUM(CASE WHEN e.account_id = 2000 THEN (e.debit - e.credit) ELSE 0 END) AS payable_change
                FROM partners p
                JOIN transactions t ON p.id = t.partner_id
                JOIN entries e ON t.id = e.transaction_id
                WHERE p.id = ?
                  AND e.account_id IN (1100, 2000)
                GROUP BY t.id
                ORDER BY t.date DESC, t.id DESC
            """

            history_rows = conn.execute(history_query, (partner_id,)).fetchall()

        transactions: list[dict[str, Any]] = []
        for row in history_rows:
            receivable_change = (row["receivable_change"] or 0.0)
            payable_change = (row["payable_change"] or 0.0)
            transactions.append(
                {
                    "date": row["date"],
                    "description": row["description"],
                    "receivable_change": round(receivable_change, 2),
                    "payable_change": round(payable_change, 2),
                    "net_change": round(receivable_change - payable_change, 2),
                }
            )

        return PartnerBalance(
            partner_name=partner_name,
            receivable=round(receivable, 2),
            payable=round(payable, 2),
            net_balance=round(receivable - payable, 2),
            transactions=transactions,
        )