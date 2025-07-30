"""
Command-line interface for the Expense Tracker application.
"""

import argparse
import sys
from datetime import date
from typing import Optional, List
from .transaction_manager import transaction_manager
from .reports import report_generator
from .validators import Validators
from .date_utils import DateUtils


class ExpenseTrackerCLI:
    """Command-line interface for the expense tracker."""
    
    def __init__(self):
        self.tm = transaction_manager
        self.rg = report_generator
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Daily Expense and Income Tracker",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Add an expense
  python -m expense_tracker add expense 25.50 --category 1 --description "Lunch" --date today
  
  # Add income
  python -m expense_tracker add income 1000 --category 11 --description "Salary" --date yesterday
  
  # View today's transactions
  python -m expense_tracker list --date today
  
  # Generate monthly report
  python -m expense_tracker report monthly
  
  # View categories
  python -m expense_tracker categories list
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add transaction command
        add_parser = subparsers.add_parser('add', help='Add a new transaction')
        add_parser.add_argument('type', choices=['expense', 'income'], help='Transaction type')
        add_parser.add_argument('amount', type=str, help='Transaction amount')
        add_parser.add_argument('--category', '-c', type=int, help='Category ID')
        add_parser.add_argument('--description', '-d', type=str, help='Transaction description')
        add_parser.add_argument('--date', type=str, default='today', help='Transaction date (default: today)')
        
        # List transactions command
        list_parser = subparsers.add_parser('list', help='List transactions')
        list_parser.add_argument('--date', type=str, help='Specific date or date range')
        list_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by transaction type')
        list_parser.add_argument('--category', type=int, help='Filter by category ID')
        list_parser.add_argument('--limit', type=int, default=50, help='Maximum number of transactions to show')
        list_parser.add_argument('--search', type=str, help='Search in descriptions and categories')
        
        # Update transaction command
        update_parser = subparsers.add_parser('update', help='Update a transaction')
        update_parser.add_argument('id', type=int, help='Transaction ID')
        update_parser.add_argument('--type', choices=['expense', 'income'], help='New transaction type')
        update_parser.add_argument('--amount', type=str, help='New amount')
        update_parser.add_argument('--category', type=int, help='New category ID')
        update_parser.add_argument('--description', type=str, help='New description')
        update_parser.add_argument('--date', type=str, help='New date')
        
        # Delete transaction command
        delete_parser = subparsers.add_parser('delete', help='Delete a transaction')
        delete_parser.add_argument('id', type=int, help='Transaction ID')
        delete_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        
        # Reports command
        report_parser = subparsers.add_parser('report', help='Generate reports')
        report_parser.add_argument('type', choices=['daily', 'weekly', 'monthly', 'yearly', 'category', 'comparison'], help='Report type')
        report_parser.add_argument('--date', type=str, help='Target date for the report')
        report_parser.add_argument('--category', type=int, help='Category ID for category report')
        report_parser.add_argument('--start', type=str, help='Start date for date range reports')
        report_parser.add_argument('--end', type=str, help='End date for date range reports')
        report_parser.add_argument('--compare-start', type=str, help='Comparison period start date')
        report_parser.add_argument('--compare-end', type=str, help='Comparison period end date')
        
        # Categories command
        categories_parser = subparsers.add_parser('categories', help='Manage categories')
        categories_subparsers = categories_parser.add_subparsers(dest='categories_action', help='Category actions')
        
        # List categories
        categories_subparsers.add_parser('list', help='List all categories')
        
        # Add category
        add_cat_parser = categories_subparsers.add_parser('add', help='Add a new category')
        add_cat_parser.add_argument('name', type=str, help='Category name')
        add_cat_parser.add_argument('type', choices=['expense', 'income'], help='Category type')
        
        # Delete category
        del_cat_parser = categories_subparsers.add_parser('delete', help='Delete a category')
        del_cat_parser.add_argument('id', type=int, help='Category ID')
        del_cat_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        
        # Summary command
        summary_parser = subparsers.add_parser('summary', help='Show summary statistics')
        summary_parser.add_argument('--start', type=str, help='Start date')
        summary_parser.add_argument('--end', type=str, help='End date')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search transactions')
        search_parser.add_argument('query', type=str, help='Search query')
        search_parser.add_argument('--limit', type=int, default=20, help='Maximum results to show')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None):
        """Run the CLI application."""
        parser = self.create_parser()
        
        if args is None:
            args = sys.argv[1:]
        
        if not args:
            parser.print_help()
            return
        
        parsed_args = parser.parse_args(args)
        
        try:
            if parsed_args.command == 'add':
                self.handle_add_transaction(parsed_args)
            elif parsed_args.command == 'list':
                self.handle_list_transactions(parsed_args)
            elif parsed_args.command == 'update':
                self.handle_update_transaction(parsed_args)
            elif parsed_args.command == 'delete':
                self.handle_delete_transaction(parsed_args)
            elif parsed_args.command == 'report':
                self.handle_generate_report(parsed_args)
            elif parsed_args.command == 'categories':
                self.handle_categories(parsed_args)
            elif parsed_args.command == 'summary':
                self.handle_summary(parsed_args)
            elif parsed_args.command == 'search':
                self.handle_search(parsed_args)
            else:
                parser.print_help()
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def handle_add_transaction(self, args):
        """Handle adding a new transaction."""
        # Validate amount
        is_valid_amount, amount, amount_error = Validators.validate_amount(args.amount)
        if not is_valid_amount:
            print(f"❌ {amount_error}")
            return
        
        # Validate date
        is_valid_date, transaction_date, date_error = Validators.validate_date_input(args.date)
        if not is_valid_date:
            print(f"❌ {date_error}")
            return
        
        # Add transaction
        success, transaction_id, message = self.tm.add_transaction(
            transaction_type=args.type,
            amount=amount,
            category_id=args.category,
            description=args.description,
            transaction_date=transaction_date
        )
        
        if success:
            print(f"✅ {message} (ID: {transaction_id})")
            
            # Show the added transaction
            transaction = self.tm.get_transaction_by_id(transaction_id)
            if transaction:
                print(f"📝 {transaction}")
        else:
            print(f"❌ {message}")
    
    def handle_list_transactions(self, args):
        """Handle listing transactions."""
        start_date = None
        end_date = None
        
        # Parse date or date range
        if args.date:
            # Try parsing as date range first
            date_range = DateUtils.parse_date_range(args.date)
            if date_range:
                start_date, end_date = date_range
            else:
                # Try parsing as single date
                parsed_date = DateUtils.parse_date(args.date)
                if parsed_date:
                    start_date = end_date = parsed_date
                else:
                    print(f"❌ Invalid date format: {args.date}")
                    return
        
        # Handle search
        if args.search:
            transactions = self.tm.search_transactions(args.search, args.limit)
        else:
            transactions = self.tm.get_transactions(
                start_date=start_date,
                end_date=end_date,
                transaction_type=args.type,
                category_id=args.category,
                limit=args.limit
            )
        
        if not transactions:
            print("📭 No transactions found.")
            return
        
        # Display transactions
        print(f"📋 Found {len(transactions)} transaction(s):")
        print("-" * 60)
        
        for transaction in transactions:
            print(transaction)
        
        # Show summary if date range is specified
        if start_date and end_date:
            print("\n" + "=" * 60)
            summary = self.tm.get_transaction_summary(start_date, end_date)
            print(summary)
    
    def handle_update_transaction(self, args):
        """Handle updating a transaction."""
        # Check if transaction exists
        existing = self.tm.get_transaction_by_id(args.id)
        if not existing:
            print(f"❌ Transaction with ID {args.id} not found.")
            return
        
        print(f"📝 Current transaction: {existing}")
        
        # Prepare update parameters
        update_params = {}
        
        if args.type:
            update_params['transaction_type'] = args.type
        
        if args.amount:
            is_valid_amount, amount, amount_error = Validators.validate_amount(args.amount)
            if not is_valid_amount:
                print(f"❌ {amount_error}")
                return
            update_params['amount'] = amount
        
        if args.category is not None:
            update_params['category_id'] = args.category
        
        if args.description is not None:
            update_params['description'] = args.description
        
        if args.date:
            is_valid_date, transaction_date, date_error = Validators.validate_date_input(args.date)
            if not is_valid_date:
                print(f"❌ {date_error}")
                return
            update_params['transaction_date'] = transaction_date
        
        if not update_params:
            print("❌ No updates provided.")
            return
        
        # Update transaction
        success, message = self.tm.update_transaction(args.id, **update_params)
        
        if success:
            print(f"✅ {message}")
            
            # Show updated transaction
            updated = self.tm.get_transaction_by_id(args.id)
            if updated:
                print(f"📝 Updated: {updated}")
        else:
            print(f"❌ {message}")
    
    def handle_delete_transaction(self, args):
        """Handle deleting a transaction."""
        # Check if transaction exists
        existing = self.tm.get_transaction_by_id(args.id)
        if not existing:
            print(f"❌ Transaction with ID {args.id} not found.")
            return
        
        print(f"📝 Transaction to delete: {existing}")
        
        # Confirm deletion
        if not args.confirm:
            response = input("❓ Are you sure you want to delete this transaction? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Deletion cancelled.")
                return
        
        # Delete transaction
        success, message = self.tm.delete_transaction(args.id)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def handle_generate_report(self, args):
        """Handle generating reports."""
        target_date = None
        if args.date:
            target_date = DateUtils.parse_date(args.date)
            if not target_date:
                print(f"❌ Invalid date format: {args.date}")
                return
        
        try:
            if args.type == 'daily':
                report_data = self.rg.generate_daily_report(target_date)
                report_text = self.rg.format_report_text(report_data, 'daily')
            
            elif args.type == 'weekly':
                report_data = self.rg.generate_weekly_report(target_date)
                report_text = self.rg.format_report_text(report_data, 'weekly')
            
            elif args.type == 'monthly':
                report_data = self.rg.generate_monthly_report(target_date)
                report_text = self.rg.format_report_text(report_data, 'monthly')
            
            elif args.type == 'yearly':
                report_data = self.rg.generate_yearly_report(target_date)
                report_text = self.rg.format_report_text(report_data, 'yearly')
            
            elif args.type == 'category':
                if not args.category:
                    print("❌ Category ID is required for category reports.")
                    return
                
                start_date = DateUtils.parse_date(args.start) if args.start else None
                end_date = DateUtils.parse_date(args.end) if args.end else None
                
                report_data = self.rg.generate_category_report(args.category, start_date, end_date)
                report_text = self.rg.format_report_text(report_data, 'category')
            
            elif args.type == 'comparison':
                if not all([args.start, args.end, args.compare_start, args.compare_end]):
                    print("❌ Comparison reports require --start, --end, --compare-start, and --compare-end dates.")
                    return
                
                period1_start = DateUtils.parse_date(args.start)
                period1_end = DateUtils.parse_date(args.end)
                period2_start = DateUtils.parse_date(args.compare_start)
                period2_end = DateUtils.parse_date(args.compare_end)
                
                if not all([period1_start, period1_end, period2_start, period2_end]):
                    print("❌ Invalid date format in comparison dates.")
                    return
                
                report_data = self.rg.generate_comparison_report(
                    period1_start, period1_end, period2_start, period2_end
                )
                report_text = self.rg.format_report_text(report_data, 'comparison')
            
            else:
                print(f"❌ Unknown report type: {args.type}")
                return
            
            print(report_text)
        
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def handle_categories(self, args):
        """Handle category management."""
        if args.categories_action == 'list':
            categories = self.tm.get_categories()
            
            if not categories:
                print("📭 No categories found.")
                return
            
            print("📂 Categories:")
            print("-" * 50)
            
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
        
        elif args.categories_action == 'add':
            success, category_id, message = self.tm.add_category(args.name, args.type)
            
            if success:
                print(f"✅ {message} (ID: {category_id})")
            else:
                print(f"❌ {message}")
        
        elif args.categories_action == 'delete':
            # Check if category exists
            category = self.tm.get_category_by_id(args.id)
            if not category:
                print(f"❌ Category with ID {args.id} not found.")
                return
            
            print(f"📂 Category to delete: {category['name']} ({category['type']})")
            
            # Confirm deletion
            if not args.confirm:
                response = input("❓ Are you sure you want to delete this category? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("❌ Deletion cancelled.")
                    return
            
            success, message = self.tm.delete_category(args.id)
            
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        
        else:
            print("❌ Unknown categories action. Use 'list', 'add', or 'delete'.")
    
    def handle_summary(self, args):
        """Handle summary statistics."""
        start_date = None
        end_date = None
        
        if args.start:
            start_date = DateUtils.parse_date(args.start)
            if not start_date:
                print(f"❌ Invalid start date format: {args.start}")
                return
        
        if args.end:
            end_date = DateUtils.parse_date(args.end)
            if not end_date:
                print(f"❌ Invalid end date format: {args.end}")
                return
        
        summary = self.tm.get_transaction_summary(start_date, end_date)
        category_summary = self.tm.get_category_summary(start_date, end_date)
        
        print("📊 Summary Statistics")
        print("=" * 50)
        print(summary)
        
        if category_summary:
            print("\n📂 Top Categories:")
            print("-" * 30)
            for category in category_summary[:10]:
                print(category)
    
    def handle_search(self, args):
        """Handle transaction search."""
        is_valid, error_msg = Validators.validate_search_query(args.query)
        if not is_valid:
            print(f"❌ {error_msg}")
            return
        
        transactions = self.tm.search_transactions(args.query, args.limit)
        
        if not transactions:
            print(f"📭 No transactions found matching '{args.query}'.")
            return
        
        print(f"🔍 Found {len(transactions)} transaction(s) matching '{args.query}':")
        print("-" * 60)
        
        for transaction in transactions:
            print(transaction)


def main():
    """Main entry point for the CLI."""
    cli = ExpenseTrackerCLI()
    cli.run()


if __name__ == '__main__':
    main()

