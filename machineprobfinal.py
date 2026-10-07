import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_FILENAME = "transactions.csv"
PROGRAM_TITLE = "S.A.C.K. EXPENSE TRACKER & BUDGET MANAGER"

CSV_HEADER = [
    "name",
    "date",
    "category",
    "amount",
    "description"
]

VALID_CATEGORIES = [
    "Food",
    "Transportation",
    "Housing & Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Personal Care",
    "Education",
    "Miscellaneous"
]

DEFAULT_BUDGETS = {
    "Food": 5000.00,
    "Transportation": 3000.00,
    "Housing & Utilities": 10000.00,
    "Entertainment": 3000.00,
    "Healthcare": 3000.00,
    "Shopping": 5000.00,
    "Personal Care": 3000.00,
    "Education": 3000.00,
    "Miscellaneous": 3000.00
}


def validate_transaction_data(
    name: str,
    date_str: str,
    category: str,
    amount_raw: Any
) -> List[str]:
    errors = []

    if not name.strip():
        errors.append("Name cannot be empty.")

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        errors.append("Date must follow YYYY-MM-DD format.")

    if category not in VALID_CATEGORIES:
        errors.append("Invalid category.")

    try:
        amount = float(amount_raw)
        if amount <= 0:
            errors.append("Amount must be greater than 0.")
    except (ValueError, TypeError):
        errors.append("Amount must be a valid number.")

    return errors


def create_transaction(
    name: str,
    date_str: str,
    category: str,
    amount: float,
    description: str = ""
) -> Dict[str, Any]:
    return {
        "name": name.strip(),
        "date": date_str,
        "category": category,
        "amount": float(amount),
        "description": description.strip()
    }


def format_transaction(transaction: Dict[str, Any]) -> str:
    return (
        f"{transaction['name']} | "
        f"{transaction['date']} | "
        f"{transaction['category']} | "
        f"₱{transaction['amount']:,.2f} | "
        f"{transaction['description']}"
    )


def calculate_total_expenses(
    transactions: List[Dict[str, Any]]
) -> float:
    return sum(transaction["amount"] for transaction in transactions)


def get_category_summary(
    transactions: List[Dict[str, Any]]
) -> Dict[str, Dict[str, float]]:
    total_expenses = calculate_total_expenses(transactions)
    summary = {}

    for category in VALID_CATEGORIES:
        category_total = sum(
            transaction["amount"]
            for transaction in transactions
            if transaction["category"] == category
        )

        category_count = sum(
            1
            for transaction in transactions
            if transaction["category"] == category
        )

        percentage = (
            (category_total / total_expenses) * 100
            if total_expenses > 0
            else 0
        )

        summary[category] = {
            "total": category_total,
            "count": category_count,
            "percentage": percentage
        }

    return summary


def filter_transactions(
    transactions: List[Dict[str, Any]],
    filter_by: str,
    criteria: Any
) -> List[Dict[str, Any]]:
    if filter_by == "category":
        return [
            transaction
            for transaction in transactions
            if transaction["category"].lower() == str(criteria).lower()
        ]

    elif filter_by == "date_range":
        start_date, end_date = criteria

        return [
            transaction
            for transaction in transactions
            if start_date <= transaction["date"] <= end_date
        ]

    elif filter_by == "keyword":
        keyword = str(criteria).lower()

        return [
            transaction
            for transaction in transactions
            if keyword in transaction["name"].lower()
            or keyword in transaction["description"].lower()
        ]

    elif filter_by == "min_amount":
        try:
            minimum = float(criteria)
        except (ValueError, TypeError):
            return []

        return [
            transaction
            for transaction in transactions
            if transaction["amount"] >= minimum
        ]

    return []


def calculate_budget_variance(
    transactions: List[Dict[str, Any]],
    category_budgets: Dict[str, float]
) -> Dict[str, Dict[str, Any]]:
    summary = get_category_summary(transactions)
    variance = {}

    for category in VALID_CATEGORIES:
        budget = category_budgets.get(category, 0)
        actual = summary[category]["total"]
        remaining = budget - actual

        if actual > budget:
            status = "OVER BUDGET"
        elif budget > 0 and actual >= budget * 0.8:
            status = "NEAR LIMIT"
        else:
            status = "WITHIN BUDGET"

        variance[category] = {
            "budget": budget,
            "actual": actual,
            "remaining": remaining,
            "status": status
        }

    return variance


def parse_file_data(
    raw_data: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    transactions = []

    for row in raw_data:
        try:
            transaction = {
                "name": row["name"],
                "date": row["date"],
                "category": row["category"],
                "amount": float(row["amount"]),
                "description": row.get("description", "")
            }

            transactions.append(transaction)

        except (KeyError, ValueError):
            continue

    return transactions


def load_transactions_from_file(
    filename: str = DATA_FILENAME
) -> List[Dict[str, Any]]:
    path = Path(filename)

    if not path.exists():
        return []

    try:
        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            raw_data = list(reader)

        return parse_file_data(raw_data)

    except (OSError, csv.Error):
        print("Error reading transaction file.")
        return []


def save_transactions_to_file(
    transactions: List[Dict[str, Any]],
    filename: str = DATA_FILENAME
) -> bool:
    try:
        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=CSV_HEADER
            )

            writer.writeheader()

            for transaction in transactions:
                writer.writerow(transaction)

        return True

    except OSError:
        print("Error saving transaction file.")
        return False


def display_main_menu() -> None:
    print("\n" + "=" * 60)
    print(f"        {PROGRAM_TITLE}")
    print("=" * 60)

    print("[1]  Add New Transaction")
    print("[2]  View All Transactions")
    print("[3]  Edit Transaction")
    print("[4]  Delete Transaction")
    print("[5]  View Category Spending Summary")
    print("[6]  Filter/Search Transactions")
    print("[7]  View Total Expenses")
    print("[8]  Budget Variance Report")
    print("[9]  Set Category Budget")
    print("[10] Plot Spending Chart")
    print("[11] Spending Insights")
    print("[0]  Save & Exit")

    print("=" * 60)


def prompt_user_input(
    prompt_text: str,
    expected_type=str
) -> Any:
    while True:
        value = input(prompt_text).strip()

        if expected_type == str:
            return value

        try:
            return expected_type(value)

        except ValueError:
            print("Invalid input. Please try again.")


def display_categories() -> None:
    print("\nAvailable Categories:")

    for index, category in enumerate(VALID_CATEGORIES, start=1):
        print(f"{index}. {category}")


def choose_category() -> str:
    display_categories()

    while True:
        choice = input("Choose category number: ").strip()

        try:
            index = int(choice)

            if 1 <= index <= len(VALID_CATEGORIES):
                return VALID_CATEGORIES[index - 1]

            print("Please choose a valid category number.")

        except ValueError:
            print("Please enter a number.")


def prompt_valid_date(
    prompt_text: str,
    allow_blank: bool = False
) -> str:
    while True:
        date_str = input(prompt_text).strip()

        if allow_blank and date_str == "":
            return ""

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str

        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")


def display_transactions_table(
    transactions: List[Dict[str, Any]]
) -> None:
    if not transactions:
        print("\nNo transactions found.")
        return

    print("\n" + "=" * 100)

    print(
        f"{'#':<4}"
        f"{'Name':<20}"
        f"{'Date':<13}"
        f"{'Category':<25}"
        f"{'Amount':>12}"
    )

    print("-" * 100)

    for index, transaction in enumerate(transactions, start=1):
        print(
            f"{index:<4}"
            f"{transaction['name'][:19]:<20}"
            f"{transaction['date']:<13}"
            f"{transaction['category'][:24]:<25}"
            f"₱{transaction['amount']:>10,.2f}"
        )

    print("=" * 100)


def add_transaction(
    transactions: List[Dict[str, Any]]
) -> None:
    print("\n========== ADD TRANSACTION ==========")

    name = input("Expense name: ").strip()

    date_str = prompt_valid_date(
        "Date (YYYY-MM-DD): "
    )

    category = choose_category()

    amount = prompt_user_input(
        "Amount: ₱",
        float
    )

    description = input(
        "Description (optional): "
    ).strip()

    errors = validate_transaction_data(
        name,
        date_str,
        category,
        amount
    )

    if errors:
        print("\nTransaction could not be added:")

        for error in errors:
            print(f"- {error}")

        return

    transaction = create_transaction(
        name,
        date_str,
        category,
        amount,
        description
    )

    transactions.append(transaction)

    print("\n✓ Transaction added successfully!")


def edit_transaction(
    transactions: List[Dict[str, Any]]
) -> None:
    if not transactions:
        print("\nNo transactions available.")
        return

    display_transactions_table(transactions)

    index = prompt_user_input(
        "Enter transaction number to edit: ",
        int
    )

    if not 1 <= index <= len(transactions):
        print("Invalid transaction number.")
        return

    transaction = transactions[index - 1]

    print("\nPress Enter to keep the current value.")

    name = input(
        f"Name [{transaction['name']}]: "
    ).strip()

    date_str = prompt_valid_date(
        f"Date [{transaction['date']}]: ",
        allow_blank=True
    )

    print("\nCurrent category:", transaction["category"])

    change_category = input(
        "Change category? (y/n): "
    ).strip().lower()

    if change_category == "y":
        category = choose_category()
    else:
        category = transaction["category"]

    amount_input = input(
        f"Amount [₱{transaction['amount']:,.2f}]: "
    ).strip()

    description = input(
        f"Description [{transaction['description']}]: "
    ).strip()

    if name == "":
        name = transaction["name"]

    if date_str == "":
        date_str = transaction["date"]

    if amount_input == "":
        amount = transaction["amount"]
    else:
        try:
            amount = float(amount_input)
        except ValueError:
            print("Invalid amount.")
            return

    if description == "":
        description = transaction["description"]

    errors = validate_transaction_data(
        name,
        date_str,
        category,
        amount
    )

    if errors:
        print("\nTransaction could not be updated:")

        for error in errors:
            print(f"- {error}")

        return

    transactions[index - 1] = create_transaction(
        name,
        date_str,
        category,
        amount,
        description
    )

    print("\n✓ Transaction updated successfully!")


def delete_transaction(
    transactions: List[Dict[str, Any]]
) -> None:
    if not transactions:
        print("\nNo transactions available.")
        return

    display_transactions_table(transactions)

    index = prompt_user_input(
        "Enter transaction number to delete: ",
        int
    )

    if not 1 <= index <= len(transactions):
        print("Invalid transaction number.")
        return

    transaction = transactions[index - 1]

    confirm = input(
        f"Delete '{transaction['name']}'? (y/n): "
    ).strip().lower()

    if confirm == "y":
        transactions.pop(index - 1)
        print("\n✓ Transaction deleted successfully!")

    else:
        print("\nDeletion cancelled.")


def show_category_summary(
    transactions: List[Dict[str, Any]]
) -> None:
    if not transactions:
        print("\nNo transactions available.")
        return

    summary = get_category_summary(transactions)

    print("\n========== CATEGORY SPENDING SUMMARY ==========")

    print(
        f"{'Category':<25}"
        f"{'Total':>15}"
        f"{'Count':>10}"
        f"{'Percentage':>15}"
    )

    print("-" * 65)

    for category in VALID_CATEGORIES:
        data = summary[category]

        print(
            f"{category:<25}"
            f"₱{data['total']:>13,.2f}"
            f"{data['count']:>10}"
            f"{data['percentage']:>13.2f}%"
        )

    print("=" * 65)


def search_transactions(
    transactions: List[Dict[str, Any]]
) -> None:
    if not transactions:
        print("\nNo transactions available.")
        return

    print("\n========== SEARCH / FILTER ==========")
    print("[1] Category")
    print("[2] Keyword")
    print("[3] Minimum Amount")
    print("[4] Date Range")

    choice = prompt_user_input(
        "Choose filter: ",
        int
    )

    results = []

    if choice == 1:
        category = choose_category()

        results = filter_transactions(
            transactions,
            "category",
            category
        )

    elif choice == 2:
        keyword = input(
            "Enter keyword: "
        ).strip()

        results = filter_transactions(
            transactions,
            "keyword",
            keyword
        )

    elif choice == 3:
        minimum = prompt_user_input(
            "Minimum amount: ₱",
            float
        )

        results = filter_transactions(
            transactions,
            "min_amount",
            minimum
        )

    elif choice == 4:
        start_date = prompt_valid_date(
            "Start date (YYYY-MM-DD): "
        )

        end_date = prompt_valid_date(
            "End date (YYYY-MM-DD): "
        )

        results = filter_transactions(
            transactions,
            "date_range",
            (start_date, end_date)
        )

    else:
        print("Invalid choice.")
        return

    print(f"\nFound {len(results)} transaction(s).")

    display_transactions_table(results)


def show_total_expenses(
    transactions: List[Dict[str, Any]]
) -> None:
    total = calculate_total_expenses(transactions)

    print("\n========== TOTAL EXPENSES ==========")
    print(f"Total Expenses: ₱{total:,.2f}")


def show_budget_variance(
    transactions: List[Dict[str, Any]],
    budgets: Dict[str, float]
) -> None:
    variance = calculate_budget_variance(
        transactions,
        budgets
    )

    print("\n========== BUDGET VARIANCE REPORT ==========")

    print(
        f"{'Category':<25}"
        f"{'Budget':>15}"
        f"{'Actual':>15}"
        f"{'Remaining':>15}"
        f"{'Status':>18}"
    )

    print("-" * 90)

    for category in VALID_CATEGORIES:
        data = variance[category]

        print(
            f"{category:<25}"
            f"₱{data['budget']:>13,.2f}"
            f"₱{data['actual']:>13,.2f}"
            f"₱{data['remaining']:>13,.2f}"
            f"{data['status']:>18}"
        )

    print("=" * 90)


def set_category_budget(
    budgets: Dict[str, float]
) -> None:
    print("\n========== SET CATEGORY BUDGET ==========")

    category = choose_category()

    current_budget = budgets.get(category, 0)

    print(
        f"Current {category} budget: "
        f"₱{current_budget:,.2f}"
    )

    new_budget = prompt_user_input(
        "Enter new budget: ₱",
        float
    )

    if new_budget < 0:
        print("Budget cannot be negative.")
        return

    budgets[category] = new_budget

    print(
        f"\n✓ {category} budget updated to "
        f"₱{new_budget:,.2f}"
    )


def plot_expense_summary(
    summary_data: Dict[str, Dict[str, float]]
) -> None:
    try:
        import importlib

        plt = importlib.import_module("matplotlib.pyplot")

    except (ImportError, ModuleNotFoundError):
        print(
            "\nMatplotlib is not installed. "
            "The chart cannot be displayed."
        )
        return

    categories = []
    amounts = []

    for category, data in summary_data.items():
        if data["total"] > 0:
            categories.append(category)
            amounts.append(data["total"])

    if not amounts:
        print("\nNo spending data available for the chart.")
        return

    plt.figure(figsize=(10, 6))

    plt.bar(categories, amounts)

    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₱)")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.show()


def calculate_average_expense(
    transactions: List[Dict[str, Any]]
) -> float:
    if not transactions:
        return 0.0

    total = calculate_total_expenses(transactions)

    return total / len(transactions)


def find_highest_expense(
    transactions: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    if not transactions:
        return None

    return max(
        transactions,
        key=lambda transaction: transaction["amount"]
    )


def find_highest_spending_category(
    transactions: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    if not transactions:
        return None

    summary = get_category_summary(transactions)

    highest_category = max(
        summary,
        key=lambda category: summary[category]["total"]
    )

    if summary[highest_category]["total"] == 0:
        return None

    return {
        "category": highest_category,
        "total": summary[highest_category]["total"],
        "percentage": summary[highest_category]["percentage"]
    }


def generate_spending_insights(
    transactions: List[Dict[str, Any]],
    budgets: Dict[str, float]
) -> Dict[str, Any]:
    if not transactions:
        return {
            "average_expense": 0,
            "highest_expense": None,
            "highest_category": None,
            "budget_alerts": []
        }

    average_expense = calculate_average_expense(
        transactions
    )

    highest_expense = find_highest_expense(
        transactions
    )

    highest_category = find_highest_spending_category(
        transactions
    )

    summary = get_category_summary(transactions)

    budget_alerts = []

    for category in VALID_CATEGORIES:
        budget = budgets.get(category, 0)
        actual = summary[category]["total"]

        if budget <= 0:
            continue

        usage_percentage = (
            actual / budget
        ) * 100

        if actual > budget:
            budget_alerts.append({
                "category": category,
                "actual": actual,
                "budget": budget,
                "usage": usage_percentage,
                "status": "EXCEEDED",
                "difference": actual - budget
            })

        elif usage_percentage >= 80:
            budget_alerts.append({
                "category": category,
                "actual": actual,
                "budget": budget,
                "usage": usage_percentage,
                "status": "NEAR LIMIT",
                "difference": budget - actual
            })

    return {
        "average_expense": average_expense,
        "highest_expense": highest_expense,
        "highest_category": highest_category,
        "budget_alerts": budget_alerts
    }


def show_spending_insights(
    transactions: List[Dict[str, Any]],
    budgets: Dict[str, float]
) -> None:
    if not transactions:
        print("\nNo transactions available.")
        print(
            "Add some transactions first to generate insights."
        )
        return

    insights = generate_spending_insights(
        transactions,
        budgets
    )

    print("\n")
    print("=" * 60)
    print(f"             {PROGRAM_TITLE}")
    print("                   SPENDING INSIGHTS")
    print("=" * 60)

    print(
        f"\nAverage Expense per Transaction: "
        f"₱{insights['average_expense']:,.2f}"
    )

    highest_expense = insights["highest_expense"]

    if highest_expense:
        print(
            f"Highest Individual Expense: "
            f"₱{highest_expense['amount']:,.2f}"
        )

        print(
            f"  → {highest_expense['name']} "
            f"({highest_expense['category']})"
        )

    highest_category = insights["highest_category"]

    if highest_category:
        print(
            f"\nHighest Spending Category: "
            f"{highest_category['category']}"
        )

        print(
            f"  → ₱{highest_category['total']:,.2f} "
            f"({highest_category['percentage']:.2f}% "
            f"of total spending)"
        )

    print("\n========== BUDGET INSIGHTS ==========")

    alerts = insights["budget_alerts"]

    if not alerts:
        print("✓ All categories are currently within budget.")

    else:
        for alert in alerts:

            if alert["status"] == "EXCEEDED":
                print(
                    f"🚨 {alert['category']}: "
                    f"Budget exceeded by "
                    f"₱{alert['difference']:,.2f}"
                )

                print(
                    f"   Spending: ₱{alert['actual']:,.2f} / "
                    f"₱{alert['budget']:,.2f} "
                    f"({alert['usage']:.1f}%)"
                )

            else:
                print(
                    f"⚠️ {alert['category']}: "
                    f"{alert['usage']:.1f}% of budget used"
                )

                print(
                    f"   Remaining budget: "
                    f"₱{alert['difference']:,.2f}"
                )

    print("\n========== RECOMMENDATION ==========")

    if highest_category:
        print(
            f"💡 Your highest spending is currently "
            f"in {highest_category['category']}."
        )

    if alerts:
        print(
            "💡 Consider reviewing the categories marked "
            "as near or over their budget."
        )
    else:
        print(
            "✓ Your spending is currently within "
            "your set budgets."
        )

    print("=" * 60)


def main() -> None:
    transactions = load_transactions_from_file()
    budgets = DEFAULT_BUDGETS.copy()

    print("=" * 60)
    print(f"       {PROGRAM_TITLE}")
    print("=" * 60)

    print(
        f"Loaded {len(transactions)} transaction(s)."
    )

    while True:
        display_main_menu()

        choice = prompt_user_input(
            "Enter your choice: ",
            int
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
                budgets
            )

        elif choice == 9:
            set_category_budget(budgets)

        elif choice == 10:
            summary = get_category_summary(
                transactions
            )

            plot_expense_summary(summary)

        elif choice == 11:
            show_spending_insights(
                transactions,
                budgets
            )

        elif choice == 0:
            saved = save_transactions_to_file(
                transactions
            )

            if saved:
                print(
                    "\n✓ Transactions saved successfully."
                )

            print(f"Thank you for using {PROGRAM_TITLE}!")
            break

        else:
            print(
                "\nInvalid choice. "
                "Please select an option from the menu."
            )


if __name__ == "__main__":
    main()
