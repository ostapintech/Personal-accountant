import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "accounting.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            -- ----------------------------------------------------------------
            -- Accounts (fixed chart of accounts)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS accounts (
                id      INTEGER PRIMARY KEY,
                name    TEXT    NOT NULL,
                type    TEXT    NOT NULL CHECK (type IN ('Asset', 'Liability', 'Revenue', 'Expense'))
            );

            -- ----------------------------------------------------------------
            -- Partners (Clients & Suppliers)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS partners (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                type    TEXT    NOT NULL CHECK (type IN ('Client', 'Supplier'))
            );

            -- ----------------------------------------------------------------
            -- Transactions (journal headers)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT    NOT NULL,          -- stored as ISO-8601: YYYY-MM-DD
                description TEXT    NOT NULL,
                partner_id  INTEGER REFERENCES partners(id) ON DELETE SET NULL
            );

            -- ----------------------------------------------------------------
            -- Entries (double-entry lines)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS entries (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id  INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
                account_id      INTEGER NOT NULL REFERENCES accounts(id),
                debit           REAL    NOT NULL DEFAULT 0 CHECK (debit  >= 0),
                credit          REAL    NOT NULL DEFAULT 0 CHECK (credit >= 0)
            );
        """)

        # Seed fixed chart of accounts (insert only if table is empty)
        existing = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        if existing == 0:
            conn.executemany(
                "INSERT INTO accounts (id, name, type) VALUES (?, ?, ?)",
                [
                    (1000, "Cash",                "Asset"),
                    (1100, "Accounts Receivable", "Asset"),
                    (2000, "Accounts Payable",    "Liability"),
                    (4000, "Revenue",              "Revenue"),
                    (5000, "Expense",              "Expense"),
                ],
            )


if __name__ == "__main__":
    init_db()
    print(f"Database initialised at: {os.path.abspath(DB_PATH)}")

    with get_connection() as conn:
        rows = conn.execute("SELECT id, name, type FROM accounts ORDER BY id").fetchall()
        print("\nChart of Accounts:")
        for r in rows:
            print(f"  {r['id']}  {r['name']:<25} {r['type']}")