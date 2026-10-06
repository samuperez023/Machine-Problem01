import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

DATA_FILENAME = "transactions.csv"

CSV_HEADER = ["name", "date", "category", "amount", "description"]

VALID_CATEGORIES = [
    "Food",
    "Transportation",
    "Housing & Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Personal Care",
    "Education",
    "Miscellaneous",
]

# Default budgets can be changed from the CLI.
DEFAULT_BUDGETS = {
    "Food": 5000.00,
    "Transportation": 3000.00,
    "Housing & Utilities": 8000.00,
    "Entertainment": 3000.00,
    "Healthcare": 3000.00,
    "Shopping": 3000.00,
    "Personal Care": 2000.00,
    "Education": 3000.00,
    "Miscellaneous": 2000.00,
}


# ============================================================
# 1. TRANSACTION OPERATIONS FUNCTIONS
# ============================================================

def validate_transaction_data(
    name: str,
    date_str: str,
    category: str,
    amount_raw: str
) -> Tuple[bool, str]:
    """Validate the data entered for a transaction."""

    clean_name = str(name).strip()
    clean_date = str(date_str).strip()
    clean_category = str(category).strip()
    clean_amount = str(amount_raw).strip()

    if not clean_name:
        return False, "Name cannot be empty."

    # Validate actual calendar date.
    try:
        datetime.strptime(clean_date, "%Y-%m-%d")
    except ValueError:
        return False, "Invalid date. Please use YYYY-MM-DD."

    if not clean_category:
        return False, "Category cannot be empty."

    if clean_category.lower() not in [c.lower() for c in VALID_CATEGORIES]:
        return False, "Please choose a category from the provided list."

    try:
        amount = float(clean_amount)
    except ValueError:
        return False, "Amount must be a valid number."

    if amount <= 0:
        return False, "Amount must be greater than zero."

    return True, "Valid"


def create_transaction(
    name: str,
    date_str: str,
    category: str,
    amount: float,
    description: str = ""
) -> Dict[str, Union[str, float]]:
    """Create and return one structured transaction record."""

    clean_description = str(description).strip()

    # Match the official category spelling.
    formatted_category = str(category).strip()
    for valid_category in VALID_CATEGORIES:
        if formatted_category.lower() == valid_category.lower():
            formatted_category = valid_category
            break

    return {
        "name": str(name).strip().title(),
        "date": str(date_str).strip(),
        "category": formatted_category,
        "amount": round(float(amount), 2),
        "description": clean_description if clean_description else "N/A",
    }


def format_transaction(transaction: Dict[str, Any]) -> str:
    """Return a clean one-line representation of a transaction."""

    return (
        f"[{transaction.get('date', 'N/A')}] "
        f"{transaction.get('name', 'N/A'):<15} | "
        f"{transaction.get('category', 'N/A'):<22} | "
        f"₱{float(transaction.get('amount', 0.0)):>10,.2f} | "
        f"{transaction.get('description', 'N/A')}"
    )


# ============================================================
# 2. BUDGET & ANALYTICS FUNCTIONS
# ============================================================

def calculate_total_expenses(
    transactions: List[Dict[str, Union[str, float]]]
) -> float:
    """Compute the total amount of all valid expenses."""

    total = 0.0

    for transaction in transactions:
        try:
            amount = float(transaction.get("amount", 0.0))
            if amount > 0:
                total += amount
        except (TypeError, ValueError):
            continue

    return round(total, 2)


def get_category_summary(
    transactions: List[Dict[str, Union[str, float]]]
) -> Dict[str, Dict[str, float]]:
    """Calculate spending totals, counts, and percentages by category."""

    summary: Dict[str, Dict[str, float]] = {}
    total_spending = calculate_total_expenses(transactions)

    for transaction in transactions:
        category = str(transaction.get("category", "Uncategorized"))

        try:
            amount = float(transaction.get("amount", 0.0))
        except (TypeError, ValueError):
            amount = 0.0

        if category not in summary:
            summary[category] = {
                "total": 0.0,
                "count": 0,
                "percentage": 0.0,
            }

        summary[category]["total"] += amount
        summary[category]["count"] += 1

    for category in summary:
        summary[category]["total"] = round(summary[category]["total"], 2)

        if total_spending > 0:
            summary[category]["percentage"] = round(
                (summary[category]["total"] / total_spending) * 100,
                2,
            )

    return summary


def filter_transactions(
    transactions: List[Dict[str, Union[str, float]]],
    filter_by: str,
    criteria: Union[str, float, Tuple[str, str]]
) -> List[Dict[str, Union[str, float]]]:
    """
    Filter transactions by:
    - category
    - date_range
    - keyword
    - min_amount
    """

    results = []
    filter_type = filter_by.lower().strip()

    for transaction in transactions:
        if filter_type == "category":
            if str(criteria).lower() in str(
                transaction.get("category", "")
            ).lower():
                results.append(transaction)

        elif filter_type == "date_range":
            if isinstance(criteria, (tuple, list)) and len(criteria) == 2:
                start_date, end_date = criteria
                transaction_date = str(transaction.get("date", ""))

                if start_date <= transaction_date <= end_date:
                    results.append(transaction)

        elif filter_type == "keyword":
            keyword = str(criteria).lower()

            searchable_text = " ".join([
                str(transaction.get("name", "")),
                str(transaction.get("category", "")),
                str(transaction.get("description", "")),
            ]).lower()

            if keyword in searchable_text:
                results.append(transaction)

        elif filter_type == "min_amount":
            try:
                minimum = float(criteria)
                if float(transaction.get("amount", 0.0)) >= minimum:
                    results.append(transaction)
            except (TypeError, ValueError):
                continue

    return results


def calculate_budget_variance(
    transactions: List[Dict[str, Union[str, float]]],
    category_budgets: Dict[str, float]
) -> Dict[str, Dict[str, float]]:
    """Compare each category's budget against its actual spending."""

    summary = get_category_summary(transactions)
    report = {}

    for category, budget in category_budgets.items():
        actual = summary.get(category, {}).get("total", 0.0)
        remaining = round(float(budget) - actual, 2)

        if remaining < 0:
            status = "EXCEEDED"
        elif remaining == 0:
            status = "On Target"
        else:
            status = "Under Budget"

        report[category] = {
            "budget": round(float(budget), 2),
            "actual": round(actual, 2),
            "remaining": remaining,
            "status": status,
        }

    return report


# ============================================================
# 3. FILE HANDLING & STORAGE FUNCTIONS
# ============================================================

def parse_file_data(
    raw_data: List[List[str]]
) -> List[Dict[str, Union[str, float]]]:
    """
    Convert raw CSV rows into internal transaction dictionaries.
    This keeps file parsing separate from the rest of the program.
    """

    transactions = []

    for row in raw_data:
        if not row or all(not str(cell).strip() for cell in row):
            continue

        # Ensure every row has the expected five columns.
        row = list(row) + [""] * (len(CSV_HEADER) - len(row))

        name = row[0].strip() or "N/A"
        date_str = row[1].strip() or "N/A"
        category = row[2].strip() or "N/A"
        description = row[4].strip() or "N/A"

        try:
            amount = float(row[3].strip())
        except (ValueError, TypeError):
            amount = 0.0

        transactions.append(
            create_transaction(
                name=name,
                date_str=date_str,
                category=category,
                amount=amount,
                description=description,
            )
        )

    return transactions


def load_transactions_from_file(
    filename: str = DATA_FILENAME
) -> List[Dict[str, Union[str, float]]]:
    """Load transactions from CSV storage."""

    file_path = Path(filename)

    if not file_path.exists():
        save_transactions_to_file([], filename)
        return []

    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)
    except (OSError, csv.Error) as error:
        print(f"[ERROR] Could not read file: {error}")
        return []

    if not rows:
        return []

    # Handle a missing or incorrect header.
    if rows[0] == CSV_HEADER:
        raw_data = rows[1:]
    else:
        raw_data = rows

    return parse_file_data(raw_data)


def save_transactions_to_file(
    transactions: List[Dict[str, Any]],
    filename: str = DATA_FILENAME
) -> bool:
    """Save all transactions to CSV storage."""

    file_path = Path(filename)

    try:
        with open(
            file_path,
            mode="w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)

            for transaction in transactions:
                writer.writerow([
                    transaction.get("name", "N/A"),
                    transaction.get("date", "N/A"),
                    transaction.get("category", "N/A"),
                    transaction.get("amount", 0.0),
                    transaction.get("description", "N/A"),
                ])

        return True

    except OSError as error:
        print(f"[ERROR] Could not save transactions: {error}")
        return False


# ============================================================
# 4. CLI & MENU NAVIGATION FUNCTIONS
# ============================================================

def display_main_menu() -> None:
    """Display the main application menu."""

    print("\n" + "=" * 70)
    print("              EXPENSE TRACKER & BUDGET MANAGER")
    print("=" * 70)
    print("[1] Add New Transaction")
    print("[2] View All Transactions")
    print("[3] Edit Transaction")
    print("[4] Delete Transaction")
    print("[5] View Category Spending Summary")
    print("[6] Filter/Search Transactions")
    print("[7] View Total Expenses")
    print("[8] Budget Variance Report")
    print("[9] Set Category Budget")
    print("[10] Plot Spending Chart")
    print("[0] Save & Exit")
    print("-" * 70)


def prompt_user_input(prompt_text: str, expected_type=str):
    """Safely read and convert user input."""

    while True:
        value = input(prompt_text).strip()

        if expected_type == str:
            return value

        if expected_type == int:
            try:
                return int(value)
            except ValueError:
                print("Invalid input. Please enter a whole number.")

        elif expected_type == float:
            try:
                return float(value)
            except ValueError:
                print("Invalid input. Please enter a number.")

        else:
            raise ValueError("Unsupported input type.")


def display_categories() -> None:
    """Display the available expense categories."""

    print("\nAvailable Categories:")
    for number, category in enumerate(VALID_CATEGORIES, start=1):
        print(f"  [{number}] {category}")


def choose_category() -> str:
    """Ask the user to select one of the valid categories."""

    display_categories()

    while True:
        choice = prompt_user_input(
            "Choose category number: ",
            int,
        )

        if 1 <= choice <= len(VALID_CATEGORIES):
            return VALID_CATEGORIES[choice - 1]

        print("Invalid category number. Please try again.")


def prompt_valid_date(prompt_text: str, allow_blank: bool = False) -> str:
    """Prompt for a valid YYYY-MM-DD date."""

    while True:
        date_str = input(prompt_text).strip()

        if allow_blank and not date_str:
            return ""

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD.")


def display_transactions_table(
    transactions: List[Dict[str, Any]]
) -> None:
    """Display transactions in an aligned ASCII table."""

    if not transactions:
        print("\nNo transactions found.")
        return

    print("\n" + "=" * 100)
    print(
        f"{'No.':<5}"
        f"{'Date':<13}"
        f"{'Name':<18}"
        f"{'Category':<23}"
        f"{'Amount':>12}  "
        f"Description"
    )
    print("-" * 100)

    for index, transaction in enumerate(transactions, start=1):
        print(
            f"{index:<5}"
            f"{transaction.get('date', 'N/A'):<13}"
            f"{transaction.get('name', 'N/A'):<18}"
            f"{transaction.get('category', 'N/A'):<23}"
            f"₱{float(transaction.get('amount', 0.0)):>10,.2f}  "
            f"{transaction.get('description', 'N/A')}"
        )

    print("=" * 100)


# ============================================================
# FEATURE HANDLERS
# These connect the CLI to the functional modules.
# ============================================================

def add_transaction(
    transactions: List[Dict[str, Union[str, float]]]
) -> None:
    """Prompt for and add a validated transaction."""

    print("\n--- ADD NEW TRANSACTION ---")

    name = prompt_user_input("Enter name: ", str)
    date_str = prompt_valid_date("Enter date (YYYY-MM-DD): ")
    category = choose_category()

    while True:
        amount_raw = prompt_user_input("Enter amount (PHP): ", str)

        valid, message = validate_transaction_data(
            name,
            date_str,
            category,
            amount_raw,
        )

        if valid:
            break

        print(f"[ERROR] {message}")

    description = prompt_user_input(
        "Enter description (optional): ",
        str,
    )

    transaction = create_transaction(
        name=name,
        date_str=date_str,
        category=category,
        amount=float(amount_raw),
        description=description,
    )

    transactions.append(transaction)

    print("\n[SUCCESS] Transaction added.")
    print(format_transaction(transaction))


def edit_transaction(
    transactions: List[Dict[str, Union[str, float]]]
) -> None:
    """Edit an existing transaction."""

    if not transactions:
        print("\nNo transactions available to edit.")
        return

    print("\n--- EDIT TRANSACTION ---")
    display_transactions_table(transactions)

    choice = prompt_user_input(
        "Enter transaction number to edit: ",
        int,
    )

    if not 1 <= choice <= len(transactions):
        print("[ERROR] Invalid transaction number.")
        return

    old = transactions[choice - 1]

    print("\nPress Enter to keep the current value.")

    name = input(f"Name [{old['name']}]: ").strip() or old["name"]

    while True:
        date_input = input(
            f"Date [{old['date']}]: "
        ).strip()

        if not date_input:
            date_str = old["date"]
            break

        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            date_str = date_input
            break
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD.")

    print(f"Current category: {old['category']}")
    category_input = input(
        "Change category? (Y/N): "
    ).strip().lower()

    if category_input == "y":
        category = choose_category()
    else:
        category = old["category"]

    while True:
        amount_input = input(
            f"Amount [{old['amount']:.2f}]: "
        ).strip()

        if not amount_input:
            amount = float(old["amount"])
            break

        try:
            amount = float(amount_input)

            if amount <= 0:
                raise ValueError

            break
        except ValueError:
            print("Amount must be a positive number.")

    description = input(
        f"Description [{old['description']}]: "
    ).strip() or old["description"]

    transactions[choice - 1] = create_transaction(
        name=name,
        date_str=date_str,
        category=category,
        amount=amount,
        description=description,
    )

    print("\n[SUCCESS] Transaction updated.")


def delete_transaction(
    transactions: List[Dict[str, Union[str, float]]]
) -> None:
    """Delete one transaction after confirmation."""

    if not transactions:
        print("\nNo transactions available to delete.")
        return

    print("\n--- DELETE TRANSACTION ---")
    display_transactions_table(transactions)

    choice = prompt_user_input(
        "Enter transaction number to delete: ",
        int,
    )

    if not 1 <= choice <= len(transactions):
        print("[ERROR] Invalid transaction number.")
        return

    selected = transactions[choice - 1]

    print("\nSelected:")
    print(format_transaction(selected))

    confirmation = input(
        "Are you sure you want to delete this transaction? (Y/N): "
    ).strip().lower()

    if confirmation == "y":
        transactions.pop(choice - 1)
        print("[SUCCESS] Transaction deleted.")
    else:
        print("Deletion cancelled.")


def show_category_summary(
    transactions: List[Dict[str, Union[str, float]]]
) -> None:
    """Display category totals and percentages."""

    summary = get_category_summary(transactions)

    if not summary:
        print("\nNo transactions available.")
        return

    print("\n--- CATEGORY SPENDING SUMMARY ---")
    print(
        f"{'Category':<25}"
        f"{'Total':>15}"
        f"{'Count':>10}"
        f"{'Share':>12}"
    )
    print("-" * 65)

    for category, data in summary.items():
        print(
            f"{category:<25}"
            f"₱{data['total']:>13,.2f}"
            f"{int(data['count']):>10}"
            f"{data['percentage']:>10.2f}%"
        )

    print("-" * 65)
    print(
        f"{'TOTAL':<25}"
        f"₱{calculate_total_expenses(transactions):>13,.2f}"
    )


def search_transactions(
    transactions: List[Dict[str, Union[str, float]]]
) -> None:
    """Provide category, keyword, date-range, and minimum-amount filters."""

    if not transactions:
        print("\nNo transactions available.")
        return

    print("\n--- FILTER / SEARCH TRANSACTIONS ---")
    print("[1] By Category")
    print("[2] By Keyword")
    print("[3] By Date Range")
    print("[4] By Minimum Amount")

    choice = prompt_user_input("Choose filter: ", int)

    if choice == 1:
        category = choose_category()
        results = filter_transactions(
            transactions,
            "category",
            category,
        )

    elif choice == 2:
        keyword = prompt_user_input(
            "Enter keyword: ",
            str,
        )
        results = filter_transactions(
            transactions,
            "keyword",
            keyword,
        )

    elif choice == 3:
        start = prompt_valid_date(
            "Start date (YYYY-MM-DD): "
        )
        end = prompt_valid_date(
            "End date (YYYY-MM-DD): "
        )

        if start > end:
            print("[ERROR] Start date cannot be later than end date.")
            return

        results = filter_transactions(
            transactions,
            "date_range",
            (start, end),
        )

    elif choice == 4:
        minimum = prompt_user_input(
            "Minimum amount (PHP): ",
            float,
        )

        if minimum < 0:
            print("[ERROR] Minimum amount cannot be negative.")
            return

        results = filter_transactions(
            transactions,
            "min_amount",
            minimum,
        )

    else:
        print("[ERROR] Invalid filter choice.")
        return

    print(f"\nFound {len(results)} transaction(s).")
    display_transactions_table(results)


def show_total_expenses(
    transactions: List[Dict[str, Union[str, float]]]
) -> None:
    """Display the current total expenses."""

    total = calculate_total_expenses(transactions)

    print("\n--- TOTAL EXPENSES ---")
    print(f"Total recorded expenses: ₱{total:,.2f}")


def show_budget_variance(
    transactions: List[Dict[str, Union[str, float]]],
    budgets: Dict[str, float]
) -> None:
    """Display actual spending versus category budgets."""

    report = calculate_budget_variance(
        transactions,
        budgets,
    )

    print("\n--- BUDGET VARIANCE REPORT ---")
    print(
        f"{'Category':<25}"
        f"{'Budget':>13}"
        f"{'Actual':>13}"
        f"{'Remaining':>15}"
        f"  Status"
    )
    print("-" * 82)

    for category, data in report.items():
        print(
            f"{category:<25}"
            f"₱{data['budget']:>11,.2f}"
            f"₱{data['actual']:>11,.2f}"
            f"₱{data['remaining']:>13,.2f}"
            f"  {data['status']}"
        )


def set_category_budget(
    budgets: Dict[str, float]
) -> None:
    """Allow the user to change a category's budget."""

    print("\n--- SET CATEGORY BUDGET ---")

    category = choose_category()

    while True:
        amount = prompt_user_input(
            f"Enter budget for {category} (PHP): ",
            float,
        )

        if amount < 0:
            print("Budget cannot be negative.")
        else:
            budgets[category] = round(amount, 2)
            print(
                f"[SUCCESS] {category} budget set to "
                f"₱{amount:,.2f}."
            )
            return


def plot_expense_summary(
    summary_data: Dict[str, Dict[str, float]]
) -> None:
    """Optional pie chart feature using Matplotlib."""

    if not summary_data:
        print("\nNo transaction summary available.")
        return

    try:
        import matplotlib.pyplot as plt  # pyright: ignore[reportMissingModuleSource]
    except ImportError:
        print("\nMatplotlib is not installed.")
        print("Install it with: pip install matplotlib")
        return

    labels = []
    sizes = []

    for category, metrics in summary_data.items():
        if metrics["total"] > 0:
            labels.append(category)
            sizes.append(metrics["total"])

    if not sizes:
        print("\nNo non-zero expenses available to plot.")
        return

    plt.figure(figsize=(8, 6))
    plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
    )
    plt.title("Expense Breakdown by Category")
    plt.tight_layout()
    plt.show()


# ============================================================
# 5. MAIN PROGRAM DRIVER
# ============================================================

def main() -> None:
    """
    Central controller of the application.

    Sequence:
    1. Load saved data.
    2. Initialize budgets.
    3. Display menu.
    4. Route the user's choice.
    5. Save changes before exit.
    """

    print("=" * 70)
    print("       WELCOME TO THE EXPENSE TRACKER & BUDGET MANAGER")
    print("=" * 70)

    # Program initialization and storage loading.
    transactions = load_transactions_from_file(DATA_FILENAME)

    # Copy default budgets so the dictionary can be changed during runtime.
    budgets = DEFAULT_BUDGETS.copy()

    print(
        f"\nLoaded {len(transactions)} saved transaction(s) "
        f"from {DATA_FILENAME}."
    )

    while True:
        display_main_menu()

        choice = prompt_user_input(
            "Enter your choice: ",
            int,
        )

        if choice == 1:
            add_transaction(transactions)

        elif choice == 2:
            display_transactions_table(transactions)

        elif choice == 3:
            edit_transaction(transactions)

        elif choice == 4:
            delete_transaction(transactions)

        elif choice == 5:
            show_category_summary(transactions)

        elif choice == 6:
            search_transactions(transactions)

        elif choice == 7:
            show_total_expenses(transactions)

        elif choice == 8:
            show_budget_variance(
                transactions,
                budgets,
            )

        elif choice == 9:
            set_category_budget(budgets)

        elif choice == 10:
            summary = get_category_summary(transactions)
            plot_expense_summary(summary)

        elif choice == 0:
            print("\nSaving transactions...")

            if save_transactions_to_file(
                transactions,
                DATA_FILENAME,
            ):
                print(
                    f"[SUCCESS] {len(transactions)} "
                    "transaction(s) saved."
                )
                print("Thank you for using Expense Tracker!")
            else:
                print(
                    "[WARNING] Program closed, but the "
                    "transactions could not be saved."
                )

            break

        else:
            print(
                "\n[ERROR] Invalid menu choice. "
                "Please choose an option from the menu."
            )


# ============================================================
# STANDARD EXECUTION BOILERPLATE
# ============================================================

if __name__ == "__main__":
    main()
