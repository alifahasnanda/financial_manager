# Financial Manager (Assignment 1)

Command-line program to view, analyze and update bank transactions from `data/transactions.csv`.

## Setup and run
Needs Python 3.9 or newer. No extra packages.

    python src/financial_manager.py

Run the checks:

    python tests/test_financial_manager.py

## Menu
1. Display all transactions
2. Check current balance
3. Show expenses by category
4. Search transactions by category
5. Add a new transaction (saved at the end of the CSV, old rows are kept)
6. Export financial summary (creates `financial_summary.txt`)
7. Set category budget (optional extension, saved in `data/budgets.json`, shows a warning when exceeded)
0. Exit

## Design choices
- Calculation functions do not use `input()` or `print()`, so they can be tested with `assert`.
- Every CSV row and every user answer is validated before it is accepted. Bad CSV rows are skipped and reported with their line number.
- New transactions are added with append mode, so existing records are never deleted.