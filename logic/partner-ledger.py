from db import get_connection
from dataclasses import dataclass

@dataclass
class PartnerBalance:
    partner_name: str
    receivable: float
    payable: float
    net_balance: float

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

        return PartnerBalance(
            partner_name=partner_name,
            receivable=round(receivable, 2),
            payable=round(payable, 2),
            net_balance=round(receivable - payable, 2)
        )