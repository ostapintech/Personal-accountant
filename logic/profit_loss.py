from db import get_connection
from dataclasses import dataclass


@dataclass
class PLReport:
    revenue: float
    expenses: float
    net_profit: float
    start_date: str
    end_date: str

class ProfitLoss:
    @staticmethod
    def get_profit_and_loss(start_date: str, end_date: str) -> PLReport:

        query = """
            SELECT 
                a.id as account_id,
                SUM(e.debit) as total_debit,
                SUM(e.credit) as total_credit
            FROM accounts a
            LEFT JOIN entries e ON a.id = e.account_id
            LEFT JOIN transactions t ON e.transaction_id = t.id
            WHERE t.date BETWEEN ? AND ?
            GROUP BY a.id
        """

        revenue = 0.0
        expenses = 0.0

        with get_connection() as conn:
            rows = conn.execute(query, (start_date, end_date)).fetchall()

            for row in rows:
                acc_id = row["account_id"]
                debit = row["total_debit"] or 0.0
                credit = row["total_credit"] or 0.0

                if acc_id == 4000:  # Revenue
                    revenue += (credit - debit)
                elif acc_id == 5000:  # Expense
                    expenses += (debit - credit)

        return PLReport(
            revenue=round(revenue, 2),
            expenses=round(expenses, 2),
            net_profit=round(revenue - expenses, 2),
            start_date=start_date,
            end_date=end_date
        )