"""Checks with assert: one normal case and boundary cases.
Run from the project folder:  python tests/test_financial_manager.py
"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import financial_manager as fm

HEADER = "date,description,category,type,amount\n"
SAMPLE = HEADER + (
    "2026-10-01,Salary,Income,income,2500.00\n"
    "2026-10-02,Rent,Housing,expense,850.00\n"
    "2026-10-04,Groceries,Food,expense,65.40\n"
    "2026-10-05,Restaurant,Entertainment,expense,32.50\n"
    "2026-10-08,Bank Transfer,Income,income,150.00\n"
    "2026-10-10,Electricity,Utilities,expense,78.90\n"
    "2026-10-12,Cinema,Entertainment,expense,24.00\n"
    "2026-10-15,Groceries,Food,expense,92.30\n"
)

with TemporaryDirectory() as folder:
    path = Path(folder) / "transactions.csv"
    path.write_text(SAMPLE, encoding="utf-8")

    # normal case: numbers match the example in the assignment
    transactions, rejected = fm.load_transactions(path)
    assert len(transactions) == 8 and rejected == []
    assert isinstance(transactions[0]["amount"], float)
    income, expenses = fm.calculate_totals(transactions)
    assert round(income, 2) == 2650.00
    assert round(expenses, 2) == 1143.10
    assert round(income - expenses, 2) == 1506.90
    by_cat = fm.expenses_by_category(transactions)
    assert round(by_cat["Housing"], 2) == 850.00
    assert round(by_cat["Food"], 2) == 157.70
    assert round(by_cat["Entertainment"], 2) == 56.50
    assert round(by_cat["Utilities"], 2) == 78.90

    # search ignores upper/lower case; unknown category gives empty list
    assert len(fm.filter_by_category(transactions, "food")) == 2
    assert fm.filter_by_category(transactions, "nothing") == []

    # add keeps the old records
    fm.append_to_csv({"date": "2026-10-20", "description": "Taxi",
                      "category": "Transport", "type": "expense", "amount": 15.5}, path)
    again, _ = fm.load_transactions(path)
    assert len(again) == 9 and again[-1]["description"] == "Taxi"

    # boundary: file without a final new line
    path.write_text(SAMPLE.rstrip("\n"), encoding="utf-8")
    fm.append_to_csv({"date": "2026-10-21", "description": "Bus",
                      "category": "Transport", "type": "expense", "amount": 2.5}, path)
    assert len(fm.load_transactions(path)[0]) == 9

    # boundary: bad rows are rejected and reported with the line number
    path.write_text(HEADER
                    + "2026-10-01,Salary,Income,income,100\n"
                    + "2026-10-02,Rent,Housing,expense,-5\n"
                    + "2026-10-03,Rent,Housing,expense,abc\n"
                    + "not-a-date,Rent,Housing,expense,5\n"
                    + "2026-10-06,Rent,Housing,gift,5\n"
                    + "2026-10-07,,Housing,expense,5\n", encoding="utf-8")
    good, bad = fm.load_transactions(path)
    assert len(good) == 1
    assert [line for line, _ in bad] == [3, 4, 5, 6, 7]

    # boundary: wrong header rejects the whole file
    path.write_text("date,amount\n2026-10-01,5\n", encoding="utf-8")
    try:
        fm.load_transactions(path)
    except ValueError:
        pass
    else:
        raise AssertionError("wrong header must be rejected")

    # budget warning
    path.write_text(SAMPLE, encoding="utf-8")
    transactions, _ = fm.load_transactions(path)
    assert fm.budget_warnings(transactions, {"Food": 100}) != []
    assert fm.budget_warnings(transactions, {"Food": 200}) == []

    # summary text
    summary = fm.build_summary(transactions)
    assert "Total Income: 2650.00 EUR" in summary
    assert "Current Balance: 1506.90 EUR" in summary

print("All checks passed")