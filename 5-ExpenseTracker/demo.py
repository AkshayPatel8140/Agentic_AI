#!/usr/bin/env python3
"""
Demo script for the Daily Expense & Income Tracker.
Shows basic functionality and usage examples.
"""

import os
import sys
from datetime import date, timedelta
from database import Database
from transaction_manager import TransactionManager
from reports import ReportGenerator
from date_utils import DateUtils


def run_demo():
    """Run a demonstration of the expense tracker."""
    print("💰 Daily Expense & Income Tracker - Demo")
    print("=" * 50)
    print()
    
    # Use a demo database
    demo_db_path = "demo_expense_tracker.db"
    
    # Remove existing demo database
    if os.path.exists(demo_db_path):
        os.remove(demo_db_path)
    
    # Initialize components
    db = Database(demo_db_path)
    tm = TransactionManager()
    tm.db = db
    rg = ReportGenerator()
    rg.tm = tm
    
    print("✅ Database initialized with default categories")
    print()
    
    # Show categories
    print("📂 Available Categories:")
    categories = tm.get_categories()
    expense_categories = [c for c in categories if c['type'] == 'expense']
    income_categories = [c for c in categories if c['type'] == 'income']
    
    print("💸 Expense Categories:")
    for cat in expense_categories[:5]:  # Show first 5
        print(f"  {cat['id']:2d}. {cat['name']}")
    print(f"  ... and {len(expense_categories) - 5} more")
    print()
    
    print("💰 Income Categories:")
    for cat in income_categories[:3]:  # Show first 3
        print(f"  {cat['id']:2d}. {cat['name']}")
    print(f"  ... and {len(income_categories) - 3} more")
    print()
    
    # Add sample transactions
    print("📝 Adding sample transactions...")
    
    # Get category IDs
    food_category = next((c['id'] for c in expense_categories if 'Food' in c['name']), None)
    transport_category = next((c['id'] for c in expense_categories if 'Transport' in c['name']), None)
    salary_category = next((c['id'] for c in income_categories if 'Salary' in c['name']), None)
    
    # Sample transactions for the last week
    today = date.today()
    sample_transactions = [
        # Today
        ('expense', 12.50, food_category, 'Lunch at cafe', today),
        ('expense', 4.25, food_category, 'Morning coffee', today),
        ('expense', 8.75, transport_category, 'Bus fare', today),
        
        # Yesterday
        ('expense', 25.00, food_category, 'Grocery shopping', today - timedelta(days=1)),
        ('expense', 15.50, transport_category, 'Taxi ride', today - timedelta(days=1)),
        ('income', 50.00, None, 'Freelance payment', today - timedelta(days=1)),
        
        # 2 days ago
        ('expense', 35.75, food_category, 'Restaurant dinner', today - timedelta(days=2)),
        ('expense', 6.00, transport_category, 'Parking fee', today - timedelta(days=2)),
        
        # 3 days ago
        ('income', 2500.00, salary_category, 'Monthly salary', today - timedelta(days=3)),
        ('expense', 45.00, food_category, 'Weekly groceries', today - timedelta(days=3)),
        
        # 4 days ago
        ('expense', 20.00, food_category, 'Pizza delivery', today - timedelta(days=4)),
        ('expense', 12.00, transport_category, 'Gas for car', today - timedelta(days=4)),
    ]
    
    transaction_ids = []
    for trans_type, amount, category_id, description, trans_date in sample_transactions:
        success, trans_id, message = tm.add_transaction(
            transaction_type=trans_type,
            amount=amount,
            category_id=category_id,
            description=description,
            transaction_date=trans_date
        )
        if success:
            transaction_ids.append(trans_id)
            print(f"  ✅ Added: {trans_type} ${amount:.2f} - {description}")
        else:
            print(f"  ❌ Failed: {message}")
    
    print(f"\n✅ Added {len(transaction_ids)} sample transactions")
    print()
    
    # Show today's transactions
    print("📅 Today's Transactions:")
    print("-" * 30)
    today_transactions = tm.get_transactions_by_date(today)
    for transaction in today_transactions:
        print(f"  {transaction}")
    
    # Show today's summary
    today_summary = tm.get_transaction_summary(today, today)
    print(f"\n📊 Today's Summary:")
    print(f"  Income: +${today_summary.total_income:.2f}")
    print(f"  Expenses: -${today_summary.total_expenses:.2f}")
    print(f"  Net: ${today_summary.net_balance:+.2f}")
    print()
    
    # Show weekly report
    print("📊 Weekly Report:")
    print("-" * 30)
    weekly_report = rg.generate_weekly_report(today)
    weekly_text = rg.format_report_text(weekly_report, 'weekly')
    print(weekly_text)
    print()
    
    # Show category breakdown
    print("📂 Category Breakdown (This Week):")
    print("-" * 30)
    start_date, end_date = DateUtils.get_week_range(today)
    category_summary = tm.get_category_summary(start_date, end_date)
    for category in category_summary[:5]:  # Top 5 categories
        print(f"  {category}")
    print()
    
    # Demonstrate search
    print("🔍 Search Demo - Finding 'food' transactions:")
    print("-" * 30)
    search_results = tm.search_transactions('food', 5)
    for transaction in search_results:
        print(f"  {transaction}")
    print()
    
    # Demonstrate date parsing
    print("📅 Date Parsing Examples:")
    print("-" * 30)
    date_examples = [
        'today',
        'yesterday',
        '3 days ago',
        'last week',
        '2023-12-25',
        'this month'
    ]
    
    for date_str in date_examples:
        if 'month' in date_str or 'week' in date_str:
            date_range = DateUtils.parse_date_range(date_str)
            if date_range:
                start, end = date_range
                print(f"  '{date_str}' → {DateUtils.format_date(start)} to {DateUtils.format_date(end)}")
        else:
            parsed_date = DateUtils.parse_date(date_str)
            if parsed_date:
                relative = DateUtils.get_relative_date_string(parsed_date)
                print(f"  '{date_str}' → {DateUtils.format_date(parsed_date)} ({relative})")
    print()
    
    # Show CLI examples
    print("💻 Command Line Examples:")
    print("-" * 30)
    print("  # Add an expense:")
    print("  python main.py add expense 15.75 --category 1 --description 'Coffee' --date today")
    print()
    print("  # View today's transactions:")
    print("  python main.py list --date today")
    print()
    print("  # Generate monthly report:")
    print("  python main.py report monthly")
    print()
    print("  # Search transactions:")
    print("  python main.py search 'coffee'")
    print()
    
    print("🎉 Demo completed!")
    print(f"📁 Demo database saved as: {demo_db_path}")
    print("🚀 Try running the interactive mode: python main.py")
    print("📖 Or check the CLI help: python main.py --help")


if __name__ == '__main__':
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)

