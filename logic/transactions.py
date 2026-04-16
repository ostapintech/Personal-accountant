from dataclasses import dataclass
from db import get_connection


class TransactionError(Exception):
    pass


@dataclass
class Entry:
    account_id: int
    debit: float = 0.0
    credit: float = 0.0


@dataclass
class Transaction:
    date: str
    description: str
    partner_id: int | None = None

    def __init__(self, date, description, partner_id=None):
        self.date = date
        self.description = description
        self.partner_id = partner_id
        self.entries = []
        self.id = None

    # ── builder ─────────────────────────────

    def add_entry(self, account_id, debit=0.0, credit=0.0):
        if debit < 0 or credit < 0:
            raise TransactionError("Debit/Credit cannot be negative")

        self.entries.append(Entry(account_id, debit, credit))

    # ── validation ──────────────────────────────────────

    def validate(self):
        if len(self.entries) < 2:
            raise TransactionError("Need at least 2 entries")

        total_debit = sum(e.debit for e in self.entries)
        total_credit = sum(e.credit for e in self.entries)

        if total_debit == 0 and total_credit == 0:
            raise TransactionError("Amounts cannot be zero")

        if round(total_debit, 2) != round(total_credit, 2):
            raise TransactionError("Debit must equal Credit")

    # ── saving ─────────────────────────────────────

    def save(self):
        self.validate()

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO transactions (date, description, partner_id) VALUES (?, ?, ?)",
                (self.date, self.description, self.partner_id),
            )

            self.id = cursor.lastrowid

            for e in self.entries:
                cursor.execute(
                    "INSERT INTO entries (transaction_id, account_id, debit, credit) VALUES (?, ?, ?, ?)",
                    (self.id, e.account_id, e.debit, e.credit),
                )

            conn.commit()

        return self.id

    # ── load from db ─────────────────────────────────

    @staticmethod
    def get(transaction_id):
        with get_connection() as conn:
            cursor = conn.cursor()

            row = cursor.execute(
                "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
            ).fetchone()

            if not row:
                raise TransactionError("Transaction not found")

            txn = Transaction(row["date"], row["description"], row["partner_id"])
            txn.id = row["id"]

            entry_rows = cursor.execute(
                "SELECT * FROM entries WHERE transaction_id = ?", (transaction_id,)
            ).fetchall()

            for e in entry_rows:
                txn.entries.append(Entry(e["account_id"], e["debit"], e["credit"]))

        return txn

    # ── display ──────────────────────────────────────────

    def print(self):
        print(f"Transaction {self.id} | {self.date} | {self.description}")

        total_dr = 0
        total_cr = 0

        for e in self.entries:
            print(f"Account {e.account_id}: DR {e.debit} CR {e.credit}")
            total_dr += e.debit
            total_cr += e.credit

        print(f"TOTAL: DR {total_dr} CR {total_cr}")
