import csv
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "transactions.csv"
SUMMARY_PATH = BASE_DIR / "financial_summary.txt"
BUDGET_PATH = BASE_DIR / "data" / "budgets.json"

COLUMNS = ["date", "description", "category", "type", "amount"]
ALLOWED_TYPES = {"income", "expense"}


# ---------------------------------------------------------------------------
# Reading and validating the CSV file
# ---------------------------------------------------------------------------
def parse_transaction(row: dict) -> dict:
    """Validate one CSV row and return a clean transaction dictionary.

    Raises:
        ValueError: If a value is missing or invalid.
    """
    missing = [c for c in COLUMNS if not (row.get(c) or "").strip()]
    if missing:
        raise ValueError("missing values: " + ", ".join(missing))

    values = {c: row[c].strip() for c in COLUMNS}

    try:
        amount = float(values["amount"])
    except ValueError:
        raise ValueError("amount must be a number")
    try:
        datetime.strptime(values["date"], "%Y-%m-%d")
    except ValueError:
        raise ValueError("date must be in YYYY-MM-DD format")
    if amount <= 0:
        raise ValueError("amount must be greater than 0")

    tx_type = values["type"].lower()
    if tx_type not in ALLOWED_TYPES:
        raise ValueError("type must be 'income' or 'expense'")

    return {
        "date": values["date"],
        "description": values["description"],
        "category": values["category"].title(),
        "type": tx_type,
        "amount": amount,
    }


def load_transactions(path: Path = CSV_PATH) -> tuple[list[dict], list[tuple]]:
    """Read the CSV file.

    Returns:
        (accepted, rejected). accepted is a list of transaction dictionaries.
        rejected is a list of (line_number, reason) for rows that are not valid.
    """
    accepted = []
    rejected = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or set(reader.fieldnames) != set(COLUMNS):
            raise ValueError("CSV header must be: " + ",".join(COLUMNS))
        for row in reader:
            try:
                accepted.append(parse_transaction(row))
            except ValueError as error:
                rejected.append((reader.line_num, str(error)))
    return accepted, rejected


# ---------------------------------------------------------------------------
# Calculations (no input and no print inside these functions)
# ---------------------------------------------------------------------------
def calculate_totals(transactions: list[dict]) -> tuple[float, float]:
    """Return (total_income, total_expenses)."""
    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    return income, expenses


def expenses_by_category(transactions: list[dict]) -> dict:
    """Return a dictionary {category: total expense}."""
    totals = {}
    for t in transactions:
        if t["type"] == "expense":
            totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]
    return totals


def filter_by_category(transactions: list[dict], category: str) -> list[dict]:
    """Return only the transactions of one category (upper/lower case ignored)."""
    return [t for t in transactions if t["category"].lower() == category.strip().lower()]


def build_summary(transactions: list[dict]) -> str:
    """Return the text of the financial summary."""
    income, expenses = calculate_totals(transactions)
    lines = [
        "FINANCIAL SUMMARY",
        f"Total Income: {income:.2f} EUR",
        f"Total Expenses: {expenses:.2f} EUR",
        f"Current Balance: {income - expenses:.2f} EUR",
        "Expenses by Category:",
    ]
    for category, total in expenses_by_category(transactions).items():
        lines.append(f"  {category}: {total:.2f} EUR")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Budget (optional extension). Saved as JSON.
# ---------------------------------------------------------------------------
def load_budgets(path: Path = BUDGET_PATH) -> dict:
    """Return {category: maximum budget}. A missing file means no budgets yet."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_budgets(budgets: dict, path: Path = BUDGET_PATH) -> None:
    """Save the budgets to a JSON file."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(budgets, f, indent=2, ensure_ascii=False)


def budget_warnings(transactions: list[dict], budgets: dict) -> list[str]:
    """Return a warning text for every category that is over its budget."""
    spent = expenses_by_category(transactions)
    return [
        f"WARNING: {category} expenses {spent[category]:.2f} EUR "
        f"exceed the budget of {limit:.2f} EUR"
        for category, limit in budgets.items()
        if spent.get(category, 0) > limit
    ]


# ---------------------------------------------------------------------------
# Asking the user for input (every answer is checked before it is accepted)
# ---------------------------------------------------------------------------
def ask_text(label: str) -> str:
    """Ask until the user types something that is not empty."""
    while True:
        text = input(f"{label}: ").strip()
        if text:
            return text
        print(f"{label} cannot be empty.")


def ask_date() -> str:
    """Ask until the user types a valid date in YYYY-MM-DD format."""
    while True:
        text = input("Date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            print("Invalid date. Example: 2026-10-20")


def ask_type() -> str:
    """Ask until the user types income or expense."""
    while True:
        text = input("Type (income/expense): ").strip().lower()
        if text in ALLOWED_TYPES:
            return text
        print("Type must be 'income' or 'expense'.")


def ask_amount(label: str = "Amount") -> float:
    """Ask until the user types a number greater than 0."""
    while True:
        text = input(f"{label}: ").strip()
        try:
            amount = float(text)
        except ValueError:
            print("Amount must be a number. Example: 25.50")
            continue
        if amount <= 0:
            print("Amount must be greater than 0.")
            continue
        return amount


# ---------------------------------------------------------------------------
# One function for each menu option
# ---------------------------------------------------------------------------
def print_table(transactions: list[dict]) -> None:
    """Print transactions as a table."""
    if not transactions:
        print("No transactions found.")
        return
    print(f"\n{'Date':<12}{'Description':<16}{'Category':<15}{'Type':<9}{'Amount':>9}")
    print("-" * 61)
    for t in transactions:
        print(f"{t['date']:<12}{t['description']:<16}{t['category']:<15}"
              f"{t['type']:<9}{t['amount']:>9.2f}")


def display_transactions(transactions: list[dict]) -> None:
    """Menu 1: print all transactions."""
    print_table(transactions)


def check_balance(transactions: list[dict]) -> None:
    """Menu 2: print income, expenses and balance."""
    income, expenses = calculate_totals(transactions)
    print(f"\nTotal Income: {income:.2f} EUR")
    print(f"Total Expenses: {expenses:.2f} EUR")
    print(f"Current Balance: {income - expenses:.2f} EUR")


def show_expenses_by_category(transactions: list[dict], budgets: dict) -> None:
    """Menu 3: print total expenses per category (and budget warnings)."""
    totals = expenses_by_category(transactions)
    if not totals:
        print("No expenses found.")
        return
    print("\nExpenses by Category:")
    for category, total in totals.items():
        print(f"{category}: {total:.2f} EUR")
    for warning in budget_warnings(transactions, budgets):
        print(warning)


def search_by_category(transactions: list[dict]) -> None:
    """Menu 4: ask for a category and print only its transactions."""
    category = ask_text("Enter category")
    print_table(filter_by_category(transactions, category))


def append_to_csv(transaction: dict, path: Path = CSV_PATH) -> None:
    """Add one row at the end of the CSV file. Old rows are kept."""
    has_content = path.exists() and path.stat().st_size > 0
    needs_newline = has_content and not path.read_bytes().endswith(b"\n")
    with path.open("a", encoding="utf-8", newline="") as f:
        if needs_newline:
            f.write("\n")
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not has_content:
            writer.writeheader()
        writer.writerow({**transaction, "amount": f"{transaction['amount']:.2f}"})


def add_transaction(transactions: list[dict], budgets: dict) -> None:
    """Menu 5: ask for a new transaction and save it to the CSV file."""
    print("\nAdd a new transaction")
    new = {
        "date": ask_date(),
        "description": ask_text("Description"),
        "category": ask_text("Category").title(),
        "type": ask_type(),
        "amount": ask_amount(),
    }
    append_to_csv(new)
    transactions.append(new)
    print("Transaction saved.")
    for warning in budget_warnings(transactions, budgets):
        print(warning)


def export_summary(transactions: list[dict], path: Path = SUMMARY_PATH) -> None:
    """Menu 6: write financial_summary.txt."""
    with path.open("w", encoding="utf-8") as f:
        f.write(build_summary(transactions))
    print(f"Summary saved to {path.name}")


def set_budget(budgets: dict) -> None:
    """Menu 7 (optional): set a maximum spending budget for a category."""
    category = ask_text("Category").title()
    budgets[category] = ask_amount("Maximum budget (EUR)")
    save_budgets(budgets)
    print(f"Budget for {category} set to {budgets[category]:.2f} EUR.")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------
def print_menu() -> None:
    """Print the main menu."""
    print("\n=== FINANCIAL MANAGER ===")
    print("1. Display all transactions")
    print("2. Check current balance")
    print("3. Show expenses by category")
    print("4. Search transactions by category")
    print("5. Add a new transaction")
    print("6. Export financial summary")
    print("7. Set category budget (optional)")
    print("0. Exit")


def main() -> None:
    """Run the menu until the user chooses 0."""
    try:
        transactions, rejected = load_transactions()
    except FileNotFoundError:
        print(f"File not found: {CSV_PATH}")
        return
    except ValueError as error:
        print(f"Cannot read file: {error}")
        return

    for line, reason in rejected:
        print(f"Skipped line {line}: {reason}")

    budgets = load_budgets()

    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        if choice == "1":
            display_transactions(transactions)
        elif choice == "2":
            check_balance(transactions)
        elif choice == "3":
            show_expenses_by_category(transactions, budgets)
        elif choice == "4":
            search_by_category(transactions)
        elif choice == "5":
            add_transaction(transactions, budgets)
        elif choice == "6":
            export_summary(transactions)
        elif choice == "7":
            set_budget(budgets)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 0-7.")


if __name__ == "__main__":
    main()