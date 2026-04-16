We are working on accounting web app, step by step following my prompts.
Python for logic, Streamlit for UI, SQLlite for storage
Do not use ready-made accounting libraries or accounting engines.
Use a fixed chart of accounts. Do not build account management.
A reasonable starting set is:
1000 — Cash
1100 — Accounts Receivable
2000 — Accounts Payable
4000 — Revenue
5000 — Expense Output me a code
First step: Create SQLite scheme for 

Accounts:
- id
- name
- type (Asset, Liability, Revenue, Expense)

Partners:
- id
- name
- type (Client, Supplier)

Transactions:
- id
- date
- description
- partner_id

Entries:
- id
- transaction_id
- account_i
- debit- credit
__________
Output is db.py file, but without decorator in connection
____
Create Python function create_transaction(...)
Instruction:
- min 2 notes (debit/credit)
- sum debit == sum credit ` else error`
___
In output i got a function which was overload by multiple tasks, so i structured this code under an oop approach