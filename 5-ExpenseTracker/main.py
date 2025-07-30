"""
Main entry point for the Expense Tracker application.
Provides both CLI and interactive modes.
"""

import sys
import os
from datetime import date
from .cli import ExpenseTrackerCLI
from .transaction_manager import transaction_manager
from .reports import report_generator
from .date_utils import DateUtils
from .validators import Validators


def interactive_mode():
    """Run the application in interactive mode."""
    print("💰 Welcome to Daily Expense & Income Tracker!")
    print("=" * 50)
    print()
    
    tm = transaction_manager
    rg = report_generator
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. Add expense")
        print("2. Add income")
        print("3. View today's transactions")
        print("4. View transactions by date")
        print("5. Generate report")
        print("6. View categories")
        print("7. Search transactions")
        print("8. Show summary")
        print("9. Help")
        print("0. Exit")
        
        choice = input("\n👉 Enter your choice (0-9): ").strip()
        
        try:
            if choice == '1':
                add_transaction_interactive('expense')
            elif choice == '2':
                add_transaction_interactive('income')
            elif choice == '3':
                view_todays_transactions()
            elif choice == '4':
                view_transactions_by_date()
            elif choice == '5':
                generate_report_interactive()
            elif choice == '6':
                view_categories()
            elif choice == '7':
                search_transactions_interactive()
            elif choice == '8':
                show_summary_interactive()
            elif choice == '9':
                show_help()
            elif choice == '0':
                print("\n👋 Thank you for using Expense Tracker! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 0-9.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again.")


def add_transaction_interactive(transaction_type: str):
    """Add a transaction interactively."""
    print(f"\n💸 Adding {transaction_type.title()}")
    print("-" * 30)
    
    # Get amount
    while True:
        amount_str = input("💵 Enter amount: $").strip()
        is_valid, amount, error_msg = Validators.validate_amount(amount_str)
        if is_valid:
            break
        print(f"❌ {error_msg}")
    
    # Show categories
    categories = transaction_manager.get_categories(transaction_type)
    if categories:
        print(f"\n📂 Available {transaction_type} categories:")
        for category in categories:
            print(f"  {category['id']:2d}. {category['name']}")
        
        # Get category
        category_id = None
        category_input = input(f"\n📂 Select category ID (or press Enter to skip): ").strip()
        if category_input:
            is_valid, category_id, error_msg = Validators.validate_id(category_input, "Category ID")
            if not is_valid:
                print(f"❌ {error_msg}")
                category_id = None
            else:
                # Verify category exists and matches type
                category = transaction_manager.get_category_by_id(category_id)
                if not category or category['type'] != transaction_type:
                    print("❌ Invalid category for this transaction type.")
                    category_id = None
    else:
        category_id = None
    
    # Get description
    description = input("📝 Enter description (optional): ").strip()
    if not description:
        description = None
    
    # Get date
    while True:
        date_input = input("📅 Enter date (today/yesterday/YYYY-MM-DD) [today]: ").strip()
        if not date_input:
            date_input = "today"
        
        is_valid, transaction_date, error_msg = Validators.validate_date_input(date_input)
        if is_valid:
            break
        print(f"❌ {error_msg}")
    
    # Add transaction
    success, transaction_id, message = transaction_manager.add_transaction(
        transaction_type=transaction_type,
        amount=amount,
        category_id=category_id,
        description=description,
        transaction_date=transaction_date
    )
    
    if success:
        print(f"\n✅ {message}")
        transaction = transaction_manager.get_transaction_by_id(transaction_id)
        if transaction:
            print(f"📝 Added: {transaction}")
    else:
        print(f"\n❌ {message}")


def view_todays_transactions():
    """View today's transactions."""
    print("\n📅 Today's Transactions")
    print("-" * 30)
    
    today = date.today()
    transactions = transaction_manager.get_transactions_by_date(today)
    
    if not transactions:
        print("📭 No transactions found for today.")
        return
    
    for transaction in transactions:
        print(transaction)
    
    # Show summary
    summary = transaction_manager.get_transaction_summary(today, today)
    print(f"\n📊 Today's Summary:")
    print(f"Income: +${summary.total_income:.2f}")
    print(f"Expenses: -${summary.total_expenses:.2f}")
    print(f"Net: ${summary.net_balance:+.2f}")


def view_transactions_by_date():
    """View transactions by date or date range."""
    print("\n📅 View Transactions by Date")
    print("-" * 30)
    
    date_input = input("📅 Enter date or date range (e.g., 'yesterday', '2023-12-01', 'this week'): ").strip()
    
    if not date_input:
        print("❌ Date input is required.")
        return
    
    # Try parsing as date range first
    date_range = DateUtils.parse_date_range(date_input)
    if date_range:
        start_date, end_date = date_range
    else:
        # Try parsing as single date
        parsed_date = DateUtils.parse_date(date_input)
        if parsed_date:
            start_date = end_date = parsed_date
        else:
            print(f"❌ Invalid date format: {date_input}")
            return
    
    transactions = transaction_manager.get_transactions(start_date, end_date)
    
    if not transactions:
        print("📭 No transactions found for the specified date(s).")
        return
    
    print(f"\n📋 Found {len(transactions)} transaction(s):")
    for transaction in transactions:
        print(transaction)
    
    # Show summary
    summary = transaction_manager.get_transaction_summary(start_date, end_date)
    print(f"\n📊 Summary for {summary.date_range}:")
    print(f"Income: +${summary.total_income:.2f} ({summary.income_count} transactions)")
    print(f"Expenses: -${summary.total_expenses:.2f} ({summary.expense_count} transactions)")
    print(f"Net: ${summary.net_balance:+.2f}")


def generate_report_interactive():
    """Generate a report interactively."""
    print("\n📊 Generate Report")
    print("-" * 30)
    print("1. Daily report")
    print("2. Weekly report")
    print("3. Monthly report")
    print("4. Yearly report")
    
    choice = input("\n👉 Select report type (1-4): ").strip()
    
    target_date = None
    date_input = input("📅 Enter date for report (or press Enter for today): ").strip()
    if date_input:
        target_date = DateUtils.parse_date(date_input)
        if not target_date:
            print(f"❌ Invalid date format: {date_input}")
            return
    
    try:
        if choice == '1':
            report_data = report_generator.generate_daily_report(target_date)
            report_text = report_generator.format_report_text(report_data, 'daily')
        elif choice == '2':
            report_data = report_generator.generate_weekly_report(target_date)
            report_text = report_generator.format_report_text(report_data, 'weekly')
        elif choice == '3':
            report_data = report_generator.generate_monthly_report(target_date)
            report_text = report_generator.format_report_text(report_data, 'monthly')
        elif choice == '4':
            report_data = report_generator.generate_yearly_report(target_date)
            report_text = report_generator.format_report_text(report_data, 'yearly')
        else:
            print("❌ Invalid choice.")
            return
        
        print(f"\n{report_text}")
    
    except Exception as e:
        print(f"❌ Error generating report: {e}")


def view_categories():
    """View all categories."""
    print("\n📂 Categories")
    print("-" * 30)
    
    categories = transaction_manager.get_categories()
    
    if not categories:
        print("📭 No categories found.")
        return
    
    expense_categories = [c for c in categories if c['type'] == 'expense']
    income_categories = [c for c in categories if c['type'] == 'income']
    
    if expense_categories:
        print("💸 Expense Categories:")
        for category in expense_categories:
            print(f"  {category['id']:2d}. {category['name']}")
        print()
    
    if income_categories:
        print("💰 Income Categories:")
        for category in income_categories:
            print(f"  {category['id']:2d}. {category['name']}")


def search_transactions_interactive():
    """Search transactions interactively."""
    print("\n🔍 Search Transactions")
    print("-" * 30)
    
    query = input("🔍 Enter search query: ").strip()
    
    if not query:
        print("❌ Search query cannot be empty.")
        return
    
    is_valid, error_msg = Validators.validate_search_query(query)
    if not is_valid:
        print(f"❌ {error_msg}")
        return
    
    transactions = transaction_manager.search_transactions(query, 20)
    
    if not transactions:
        print(f"📭 No transactions found matching '{query}'.")
        return
    
    print(f"\n🔍 Found {len(transactions)} transaction(s) matching '{query}':")
    for transaction in transactions:
        print(transaction)


def show_summary_interactive():
    """Show summary statistics interactively."""
    print("\n📊 Summary Statistics")
    print("-" * 30)
    
    date_input = input("📅 Enter date range (or press Enter for all time): ").strip()
    
    start_date = None
    end_date = None
    
    if date_input:
        date_range = DateUtils.parse_date_range(date_input)
        if date_range:
            start_date, end_date = date_range
        else:
            parsed_date = DateUtils.parse_date(date_input)
            if parsed_date:
                start_date = end_date = parsed_date
            else:
                print(f"❌ Invalid date format: {date_input}")
                return
    
    summary = transaction_manager.get_transaction_summary(start_date, end_date)
    category_summary = transaction_manager.get_category_summary(start_date, end_date)
    
    print(f"\n{summary}")
    
    if category_summary:
        print("\n📂 Top Categories:")
        print("-" * 30)
        for category in category_summary[:10]:
            print(category)


def show_help():
    """Show help information."""
    print("\n❓ Help - Daily Expense & Income Tracker")
    print("=" * 50)
    print("""
📋 MAIN FEATURES:
• Add expenses and income with categories and descriptions
• View transactions by date or date range
• Generate daily, weekly, monthly, and yearly reports
• Search transactions by description or category
• Manage categories for better organization

📅 DATE FORMATS SUPPORTED:
• today, yesterday, tomorrow
• YYYY-MM-DD (e.g., 2023-12-25)
• DD/MM/YYYY (e.g., 25/12/2023)
• MM/DD/YYYY (e.g., 12/25/2023)
• Relative dates: "3 days ago", "last week", "last month"

📊 DATE RANGES:
• "this week", "this month", "this year"
• "last week", "last month", "last year"
• "2023-01-01 to 2023-01-31"
• "01/01/2023 - 01/31/2023"

💡 TIPS:
• Use categories to organize your transactions
• Add descriptions for better tracking
• Generate reports to analyze spending patterns
• Use search to find specific transactions quickly

🚀 COMMAND LINE MODE:
You can also use this app from the command line:
python -m expense_tracker add expense 25.50 --category 1 --description "Lunch"
python -m expense_tracker list --date today
python -m expense_tracker report monthly

For more CLI options, run: python -m expense_tracker --help
    """)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # CLI mode
        cli = ExpenseTrackerCLI()
        cli.run()
    else:
        # Interactive mode
        interactive_mode()


if __name__ == '__main__':
    main()

