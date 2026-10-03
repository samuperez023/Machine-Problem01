def validate_transaction_data(name: str, date_str: str, category: str, amount_raw: str) -> tuple[bool, str]:
    clean_name = str(name).strip()
    clean_date = str(date_str).strip()
    clean_category = str(category).strip()
    clean_amount = str(amount_raw).strip()

    if len(clean_name) == 0:
        return False, "Name cannot be empty."

    date_parts = clean_date.split("-")

    if len(date_parts) != 3:
        return False, "Invalid date format. Please use YYYY-MM-DD (e.g., 2026-10-01)."
    else:
        year, month, day = date_parts[0], date_parts[1], date_parts[2]

        if not (year.isdigit() and len(year) == 4):
            return False, "Invalid year. Year must be 4 digits."
        elif not (month.isdigit() and len(month) == 2):
            return False, "Invalid month. Month must be 2 digits."
        elif not (day.isdigit() and len(day) == 2):
            return False, "Invalid day. Day must be 2 digits."
        else:
            m = int(month)
            d = int(day)

            if m < 1 or m > 12:
                return False, "Invalid month value. Month must be between 01 and 12."
            elif d < 1 or d > 31:
                return False, "Invalid day value. Day must be between 01 and 31."

    if len(clean_category) == 0:
        return False, "Category cannot be empty."

    has_valid_dots = clean_amount.count(".") <= 1
    digits_only = clean_amount.replace(".", "", 1)

    if not (has_valid_dots and digits_only.isdigit()):
        return False, "Invalid amount. Please enter a valid positive numerical value."
    else:
        amount_val = float(clean_amount)
        if amount_val <= 0:
            return False, "Amount must be greater than zero."

    return True, "Valid"


def create_transaction(name: str, date_str: str, category: str, amount: float, description: str = "") -> dict:

    clean_desc = str(description).strip()

    if len(clean_desc) == 0:
        formatted_desc = "N/A"
    else:
        formatted_desc = clean_desc

    return {
        "name": str(name).strip().title(),
        "date": str(date_str).strip(),
        "category": str(category).strip().title(),
        "amount": round(float(amount), 2),
        "description": formatted_desc
    }


def format_transaction(transaction: dict) -> str:

    name = transaction.get("name", "N/A")
    date = transaction.get("date", "N/A")
    category = transaction.get("category", "N/A")
    amount = transaction.get("amount", 0.0)
    description = transaction.get("description", "N/A")

    return f"[{date}] | User: {name:<12} | Category: {category:<15} | Amount: ₱{amount:>8.2f} | Note: {description}"


if __name__ == "__main__":
    print("=== Expense Entry Form ===\n")

    user_name = input("Enter name: ")
    user_date = input("Enter date (YYYY-MM-DD): ")
    user_category = input("Enter category (e.g., Food, Transport): ")
    user_amount = input("Enter amount (in PHP): ")
    user_desc = input("Enter description (optional): ")

    print("\nValidating input...")

    is_valid, error_msg = validate_transaction_data(user_name, user_date, user_category, user_amount)

    if is_valid:
        new_transact = create_transaction(
            name=user_name,
            date_str=user_date,
            category=user_category,
            amount=float(user_amount),
            description=user_desc
        )
        print("\n[SUCCESS] Transaction successfully recorded!")
        print(format_transaction(new_transact))
    else:
        print(f"\n[ERROR] Could not record transaction: {error_msg}")
