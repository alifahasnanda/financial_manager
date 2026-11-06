import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "transactions.csv"


def load_transactions() -> list[dict]:
    """Read transactions.csv and return a list of dictionaries.

    Returns:
        One dictionary per row. The amount is converted to float.
    """
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [
        {"date": row["date"],
         "description": row["description"],
         "category": row["category"],
         "type": row["type"],
         "amount": float(row["amount"])}
        for row in rows
    ]


def display_transactions(transactions: list[dict]) -> None:
    """Menu 1: print all transactions."""
    print(f"\n{'Date':<12}{'Description':<16}{'Category':<15}{'Type':<9}{'Amount':>9}")
    print("-" * 61)
    for t in transactions:
        print(f"{t['date']:<12}{t['description']:<16}{t['category']:<15}"
              f"{t['type']:<9}{t['amount']:>9.2f}")


def print_menu() -> None:
    """Print the main menu."""
    print("\n=== FINANCIAL MANAGER ===")
    print("1. Display all transactions")
    print("2. Check current balance")
    print("3. Show expenses by category")
    print("4. Search transactions by category")
    print("5. Add a new transaction")
    print("6. Export financial summary")
    print("0. Exit")


def main() -> None:
    """Run the menu until the user chooses 0."""
    transactions = load_transactions()
    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        if choice == "1":
            display_transactions(transactions)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 0-6.")


if __name__ == "__main__":
    main()