"""
Expense Tracker & Budget Manager - Budget & Analytics Module
This module contains core business, calculation, aggregation, and analytics logic.
"""

from typing import List, Dict, Union, Any, Optional

# Standard spending categories used across the application
VALID_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing & Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Personal Care",
    "Education",
    "Miscellaneous"
]

# ==========================================
# CORE ANALYTICS & CALCULATION FUNCTIONS
# ==========================================

def calculate_total_expenses(transactions: List[Dict[str, Union[str, float]]]) -> float:
    """
    Computes the aggregate sum of all logged expenses.
    
    Parameters:
        transactions (list): List of transaction dictionaries.
        
    Returns:
        float: Total monetary sum of all valid transactions.
    """
    if not transactions:
        return 0.0
    
    total = 0.0
    for txn in transactions:
        # Gracefully extract and sum amount field
        amount = txn.get("amount", 0.0)
        if isinstance(amount, (int, float)) and amount > 0:
            total += float(amount)
            
    return round(total, 2)


def get_category_summary(transactions: List[Dict[str, Union[str, float]]]) -> Dict[str, Dict[str, float]]:
    """
    Aggregates total spending grouped by unique categories, calculating
    both the absolute total amount and percentage contribution for each category.
    
    Parameters:
        transactions (list): List of transaction dictionaries.
        
    Returns:
        dict: A dictionary mapping each category to its summary metrics:
              {
                  'Category Name': {
                      'total': float,
                      'count': int,
                      'percentage': float
                  }
              }
    """
    total_spending = calculate_total_expenses(transactions)
    summary = {}
    
    if not transactions:
        return summary

    # Step 1: Aggregate totals and counts per category
    for txn in transactions:
        category = txn.get("category", "Uncategorized")
        amount = float(txn.get("amount", 0.0))
        
        if category not in summary:
            summary[category] = {"total": 0.0, "count": 0, "percentage": 0.0}
            
        summary[category]["total"] += amount
        summary[category]["count"] += 1

    # Step 2: Compute percentage contributions
    for category, metrics in summary.items():
        metrics["total"] = round(metrics["total"], 2)
        if total_spending > 0:
            metrics["percentage"] = round((metrics["total"] / total_spending) * 100, 2)
        else:
            metrics["percentage"] = 0.0

    return summary


def filter_transactions(
    transactions: List[Dict[str, Union[str, float]]], 
    filter_by: str, 
    criteria: Union[str, float, tuple]
) -> List[Dict[str, Union[str, float]]]:
    """
    Returns a filtered list of transaction records based on specified criteria.
    
    Parameters:
        transactions (list): Master list of transaction records.
        filter_by (str): Property to filter on ('category', 'date_range', 'keyword', 'min_amount').
        criteria: Value to filter against:
                  - 'category': category string (e.g., 'Food & Dining')
                  - 'date_range': tuple of ('YYYY-MM-DD', 'YYYY-MM-DD')
                  - 'keyword': search term for description matching
                  - 'min_amount': minimum threshold float value
                  
    Returns:
        list: Filtered collection of transaction dictionaries.
    """
    if not transactions:
        return []
    
    filtered_results = []
    filter_type = filter_by.lower().strip()
    
    for txn in transactions:
        if filter_type == "category":
            if str(criteria).lower() in str(txn.get("category", "")).lower():
                filtered_results.append(txn)
                
        elif filter_type == "date_range":
            # Expects criteria as a tuple/list: (start_date_str, end_date_str)
            if isinstance(criteria, (tuple, list)) and len(criteria) == 2:
                start_date, end_date = criteria
                txn_date = str(txn.get("date", ""))
                if start_date <= txn_date <= end_date:
                    filtered_results.append(txn)
                    
        elif filter_type == "keyword":
            # Searches inside the transaction description field
            keyword = str(criteria).lower()
            description = str(txn.get("description", "")).lower()
            category = str(txn.get("category", "")).lower()
            if keyword in description or keyword in category:
                filtered_results.append(txn)
                
        elif filter_type == "min_amount":
            try:
                min_val = float(criteria)
                if float(txn.get("amount", 0.0)) >= min_val:
                    filtered_results.append(txn)
            except ValueError:
                continue

    return filtered_results


def calculate_budget_variance(
    transactions: List[Dict[str, Union[str, float]]], 
    category_budgets: Dict[str, float]
) -> Dict[str, Dict[str, float]]:
    """
    Compares set budget limits against actual spending per category.
    
    Parameters:
        transactions (list): List of current transaction records.
        category_budgets (dict): Mapping of category names to budget limits.
                                 e.g., {'Food & Dining': 500.0, 'Transportation': 150.0}
                                 
    Returns:
        dict: Breakdown containing budget, actual spend, remaining balance, and status.
    """
    summary = get_category_summary(transactions)
    variance_report = {}
    
    for category, budget_limit in category_budgets.items():
        actual_spend = summary.get(category, {}).get("total", 0.0)
        remaining = round(budget_limit - actual_spend, 2)
        
        status = "Under Budget"
        if remaining < 0:
            status = "EXCEEDED"
        elif remaining == 0:
            status = "On Target"
            
        variance_report[category] = {
            "budget": round(float(budget_limit), 2),
            "actual": actual_spend,
            "remaining": remaining,
            "status": status
        }
        
    return variance_report


# ==========================================
# OPTIONAL VISUALIZATION FEATURE
# ==========================================

def plot_expense_summary(summary_data: Dict[str, Dict[str, float]]) -> None:
    """
    Optional Visual Feature: Generates a graphical pie chart showing spending
    breakdown using Matplotlib. Handles missing imports gracefully if Matplotlib
    is not installed.
    
    Parameters:
        summary_data (dict): Result dictionary from get_category_summary().
    """
    if not summary_data:
        print("\n[!] No transaction summary data available to plot.")
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[!] Matplotlib library is not installed. Plotting feature unavailable.")
        print("    Install using: pip install matplotlib")
        return

    labels = []
    sizes = []

    for category, metrics in summary_data.items():
        if metrics["total"] > 0:
            labels.append(category)
            sizes.append(metrics["total"])

    if not sizes:
        print("\n[!] No non-zero expense records found to plot.")
        return

    # Render Matplotlib Pie Chart
    plt.figure(figsize=(8, 6))
    plt.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=plt.cm.Paired.colors
    )
    plt.title("Expense Breakdown by Category", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


# ==========================================
# MODULE TEST DRIVER / DEMONSTRATION
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print(" TESTING BUDGET & ANALYTICS MODULE ".center(60, "="))
    print("=" * 60)

    # Mock Data matching the schema expected from Transaction Operations
    mock_transactions = [
        {"id": 1, "date": "2026-10-01", "category": "Food & Dining", "amount": 45.50, "description": "Grocery Shopping"},
        {"id": 2, "date": "2026-10-02", "category": "Transportation", "amount": 20.00, "description": "Gas station"},
        {"id": 3, "date": "2026-10-03", "category": "Food & Dining", "amount": 15.25, "description": "Lunch with team"},
        {"id": 4, "date": "2026-10-04", "category": "Entertainment", "amount": 50.00, "description": "Movie tickets"},
        {"id": 5, "date": "2026-10-05", "category": "Housing & Utilities", "amount": 120.00, "description": "Electric bill"},
    ]

    # 1. Test Total Calculation
    total = calculate_total_expenses(mock_transactions)
    print(f"\n[1] Aggregate Expense Total: ${total:.2f}")

    # 2. Test Category Breakdown
    print("\n[2] Category Summary:")
    cat_summary = get_category_summary(mock_transactions)
    print(f"{'Category':<22} | {'Total ($)':<10} | {'Count':<6} | {'Share (%)':<8}")
    print("-" * 55)
    for cat, data in cat_summary.items():
        print(f"{cat:<22} | ${data['total']:<9.2f} | {data['count']:<6} | {data['percentage']:<7.1f}%")

    # 3. Test Filtering
    print("\n[3] Filter Test ('Food & Dining'):")
    filtered = filter_transactions(mock_transactions, filter_by="category", criteria="Food & Dining")
    for item in filtered:
        print(f"  - {item['date']} | {item['description']} (${item['amount']:.2f})")

    # 4. Test Budget Variance
    print("\n[4] Budget Variance Comparison:")
    mock_budgets = {"Food & Dining": 50.00, "Transportation": 30.00, "Entertainment": 100.00}
    variance = calculate_budget_variance(mock_transactions, mock_budgets)
    print(f"{'Category':<18} | {'Budget':<8} | {'Actual':<8} | {'Status':<12}")
    print("-" * 55)
    for cat, data in variance.items():
        print(f"{cat:<18} | ${data['budget']:<7.2f} | ${data['actual']:<7.2f} | {data['status']}")

    print("\n" + "=" * 60)
    print(" ALL ANALYTICS TESTS COMPLETED ".center(60, "="))
    print("=" * 60)
