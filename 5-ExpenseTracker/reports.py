"""
Reporting module for the Expense Tracker application.
Generates various reports and summaries.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from .transaction_manager import transaction_manager
from .models import Transaction, TransactionSummary, CategorySummary
from .date_utils import DateUtils


class ReportGenerator:
    """Generates various reports and summaries."""
    
    def __init__(self):
        self.tm = transaction_manager
    
    def generate_daily_report(self, target_date: date = None) -> Dict[str, Any]:
        """Generate a daily report for a specific date."""
        if target_date is None:
            target_date = date.today()
        
        transactions = self.tm.get_transactions_by_date(target_date)
        summary = self.tm.get_transaction_summary(target_date, target_date)
        category_summary = self.tm.get_category_summary(target_date, target_date)
        
        return {
            'date': target_date,
            'date_formatted': DateUtils.format_date(target_date, 'long'),
            'summary': summary,
            'transactions': transactions,
            'category_breakdown': category_summary,
            'transaction_count': len(transactions)
        }
    
    def generate_weekly_report(self, target_date: date = None) -> Dict[str, Any]:
        """Generate a weekly report."""
        if target_date is None:
            target_date = date.today()
        
        start_date, end_date = DateUtils.get_week_range(target_date)
        
        transactions = self.tm.get_transactions(start_date, end_date)
        summary = self.tm.get_transaction_summary(start_date, end_date)
        category_summary = self.tm.get_category_summary(start_date, end_date)
        
        # Get daily breakdown
        daily_breakdown = []
        current_date = start_date
        while current_date <= end_date:
            daily_transactions = self.tm.get_transactions_by_date(current_date)
            daily_summary = self.tm.get_transaction_summary(current_date, current_date)
            
            daily_breakdown.append({
                'date': current_date,
                'date_formatted': DateUtils.format_date(current_date, 'short'),
                'summary': daily_summary,
                'transaction_count': len(daily_transactions)
            })
            current_date += timedelta(days=1)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'week_range': f"{DateUtils.format_date(start_date)} to {DateUtils.format_date(end_date)}",
            'summary': summary,
            'transactions': transactions,
            'category_breakdown': category_summary,
            'daily_breakdown': daily_breakdown
        }
    
    def generate_monthly_report(self, target_date: date = None) -> Dict[str, Any]:
        """Generate a monthly report."""
        if target_date is None:
            target_date = date.today()
        
        start_date, end_date = DateUtils.get_month_range(target_date)
        
        transactions = self.tm.get_transactions(start_date, end_date)
        summary = self.tm.get_transaction_summary(start_date, end_date)
        category_summary = self.tm.get_category_summary(start_date, end_date)
        
        # Get weekly breakdown
        weekly_breakdown = []
        current_date = start_date
        week_num = 1
        
        while current_date <= end_date:
            week_start = current_date
            week_end = min(current_date + timedelta(days=6), end_date)
            
            week_summary = self.tm.get_transaction_summary(week_start, week_end)
            week_transactions = self.tm.get_transactions(week_start, week_end)
            
            weekly_breakdown.append({
                'week_number': week_num,
                'start_date': week_start,
                'end_date': week_end,
                'week_range': f"{DateUtils.format_date(week_start, 'short')} - {DateUtils.format_date(week_end, 'short')}",
                'summary': week_summary,
                'transaction_count': len(week_transactions)
            })
            
            current_date = week_end + timedelta(days=1)
            week_num += 1
        
        return {
            'month': target_date.strftime('%B %Y'),
            'start_date': start_date,
            'end_date': end_date,
            'summary': summary,
            'transactions': transactions,
            'category_breakdown': category_summary,
            'weekly_breakdown': weekly_breakdown
        }
    
    def generate_yearly_report(self, target_date: date = None) -> Dict[str, Any]:
        """Generate a yearly report."""
        if target_date is None:
            target_date = date.today()
        
        start_date, end_date = DateUtils.get_year_range(target_date)
        
        transactions = self.tm.get_transactions(start_date, end_date)
        summary = self.tm.get_transaction_summary(start_date, end_date)
        category_summary = self.tm.get_category_summary(start_date, end_date)
        
        # Get monthly breakdown
        monthly_breakdown = []
        current_month = start_date.replace(day=1)
        
        while current_month <= end_date:
            month_start, month_end = DateUtils.get_month_range(current_month)
            month_end = min(month_end, end_date)  # Don't go beyond the year
            
            month_summary = self.tm.get_transaction_summary(month_start, month_end)
            month_transactions = self.tm.get_transactions(month_start, month_end)
            
            monthly_breakdown.append({
                'month': current_month.strftime('%B'),
                'month_year': current_month.strftime('%B %Y'),
                'start_date': month_start,
                'end_date': month_end,
                'summary': month_summary,
                'transaction_count': len(month_transactions)
            })
            
            # Move to next month
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)
        
        return {
            'year': target_date.year,
            'start_date': start_date,
            'end_date': end_date,
            'summary': summary,
            'transactions': transactions,
            'category_breakdown': category_summary,
            'monthly_breakdown': monthly_breakdown
        }
    
    def generate_category_report(
        self,
        category_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generate a report for a specific category."""
        category = self.tm.get_category_by_id(category_id)
        if not category:
            return {'error': 'Category not found'}
        
        transactions = self.tm.get_transactions(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )
        
        if not transactions:
            return {
                'category': category,
                'transactions': [],
                'summary': {
                    'total_amount': 0,
                    'transaction_count': 0,
                    'average_amount': 0
                }
            }
        
        total_amount = sum(t.amount for t in transactions)
        average_amount = total_amount / len(transactions)
        
        # Group by date for trend analysis
        daily_totals = {}
        for transaction in transactions:
            date_key = transaction.transaction_date
            if date_key not in daily_totals:
                daily_totals[date_key] = 0
            daily_totals[date_key] += transaction.amount
        
        return {
            'category': category,
            'transactions': transactions,
            'summary': {
                'total_amount': total_amount,
                'transaction_count': len(transactions),
                'average_amount': average_amount
            },
            'daily_totals': daily_totals,
            'date_range': f"{DateUtils.format_date(start_date)} to {DateUtils.format_date(end_date)}" if start_date and end_date else "All time"
        }
    
    def generate_comparison_report(
        self,
        period1_start: date,
        period1_end: date,
        period2_start: date,
        period2_end: date
    ) -> Dict[str, Any]:
        """Generate a comparison report between two periods."""
        period1_summary = self.tm.get_transaction_summary(period1_start, period1_end)
        period2_summary = self.tm.get_transaction_summary(period2_start, period2_end)
        
        period1_categories = self.tm.get_category_summary(period1_start, period1_end)
        period2_categories = self.tm.get_category_summary(period2_start, period2_end)
        
        # Calculate changes
        income_change = period2_summary.total_income - period1_summary.total_income
        expense_change = period2_summary.total_expenses - period1_summary.total_expenses
        net_change = period2_summary.net_balance - period1_summary.net_balance
        
        # Calculate percentage changes
        income_pct_change = (income_change / period1_summary.total_income * 100) if period1_summary.total_income > 0 else 0
        expense_pct_change = (expense_change / period1_summary.total_expenses * 100) if period1_summary.total_expenses > 0 else 0
        
        return {
            'period1': {
                'start_date': period1_start,
                'end_date': period1_end,
                'range': f"{DateUtils.format_date(period1_start)} to {DateUtils.format_date(period1_end)}",
                'summary': period1_summary,
                'categories': period1_categories
            },
            'period2': {
                'start_date': period2_start,
                'end_date': period2_end,
                'range': f"{DateUtils.format_date(period2_start)} to {DateUtils.format_date(period2_end)}",
                'summary': period2_summary,
                'categories': period2_categories
            },
            'changes': {
                'income_change': income_change,
                'expense_change': expense_change,
                'net_change': net_change,
                'income_pct_change': income_pct_change,
                'expense_pct_change': expense_pct_change
            }
        }
    
    def format_report_text(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Format report data as readable text."""
        if report_type == 'daily':
            return self._format_daily_report_text(report_data)
        elif report_type == 'weekly':
            return self._format_weekly_report_text(report_data)
        elif report_type == 'monthly':
            return self._format_monthly_report_text(report_data)
        elif report_type == 'yearly':
            return self._format_yearly_report_text(report_data)
        elif report_type == 'category':
            return self._format_category_report_text(report_data)
        elif report_type == 'comparison':
            return self._format_comparison_report_text(report_data)
        else:
            return "Unknown report type"
    
    def _format_daily_report_text(self, data: Dict[str, Any]) -> str:
        """Format daily report as text."""
        lines = [
            f"📅 Daily Report - {data['date_formatted']}",
            "=" * 50,
            "",
            str(data['summary']),
            ""
        ]
        
        if data['transactions']:
            lines.append("📋 Transactions:")
            lines.append("-" * 30)
            for transaction in data['transactions']:
                lines.append(str(transaction))
            lines.append("")
        
        if data['category_breakdown']:
            lines.append("📊 Category Breakdown:")
            lines.append("-" * 30)
            for category in data['category_breakdown']:
                lines.append(str(category))
        
        return "\n".join(lines)
    
    def _format_weekly_report_text(self, data: Dict[str, Any]) -> str:
        """Format weekly report as text."""
        lines = [
            f"📅 Weekly Report - {data['week_range']}",
            "=" * 50,
            "",
            str(data['summary']),
            ""
        ]
        
        if data['daily_breakdown']:
            lines.append("📊 Daily Breakdown:")
            lines.append("-" * 30)
            for day in data['daily_breakdown']:
                lines.append(f"{day['date_formatted']}: Income: +${day['summary'].total_income:.2f}, Expenses: -${day['summary'].total_expenses:.2f}, Net: ${day['summary'].net_balance:+.2f}")
            lines.append("")
        
        if data['category_breakdown']:
            lines.append("📊 Category Breakdown:")
            lines.append("-" * 30)
            for category in data['category_breakdown']:
                lines.append(str(category))
        
        return "\n".join(lines)
    
    def _format_monthly_report_text(self, data: Dict[str, Any]) -> str:
        """Format monthly report as text."""
        lines = [
            f"📅 Monthly Report - {data['month']}",
            "=" * 50,
            "",
            str(data['summary']),
            ""
        ]
        
        if data['weekly_breakdown']:
            lines.append("📊 Weekly Breakdown:")
            lines.append("-" * 30)
            for week in data['weekly_breakdown']:
                lines.append(f"Week {week['week_number']} ({week['week_range']}): Net: ${week['summary'].net_balance:+.2f}")
            lines.append("")
        
        if data['category_breakdown']:
            lines.append("📊 Top Categories:")
            lines.append("-" * 30)
            for category in data['category_breakdown'][:10]:  # Top 10
                lines.append(str(category))
        
        return "\n".join(lines)
    
    def _format_yearly_report_text(self, data: Dict[str, Any]) -> str:
        """Format yearly report as text."""
        lines = [
            f"📅 Yearly Report - {data['year']}",
            "=" * 50,
            "",
            str(data['summary']),
            ""
        ]
        
        if data['monthly_breakdown']:
            lines.append("📊 Monthly Breakdown:")
            lines.append("-" * 30)
            for month in data['monthly_breakdown']:
                lines.append(f"{month['month']}: Net: ${month['summary'].net_balance:+.2f}")
            lines.append("")
        
        if data['category_breakdown']:
            lines.append("📊 Top Categories:")
            lines.append("-" * 30)
            for category in data['category_breakdown'][:15]:  # Top 15
                lines.append(str(category))
        
        return "\n".join(lines)
    
    def _format_category_report_text(self, data: Dict[str, Any]) -> str:
        """Format category report as text."""
        if 'error' in data:
            return f"❌ Error: {data['error']}"
        
        category = data['category']
        summary = data['summary']
        
        lines = [
            f"📊 Category Report - {category['name']} ({category['type'].title()})",
            "=" * 50,
            "",
            f"Total Amount: ${summary['total_amount']:.2f}",
            f"Transaction Count: {summary['transaction_count']}",
            f"Average Amount: ${summary['average_amount']:.2f}",
            f"Date Range: {data['date_range']}",
            ""
        ]
        
        if data['transactions']:
            lines.append("📋 Recent Transactions:")
            lines.append("-" * 30)
            for transaction in data['transactions'][-10:]:  # Last 10
                lines.append(str(transaction))
        
        return "\n".join(lines)
    
    def _format_comparison_report_text(self, data: Dict[str, Any]) -> str:
        """Format comparison report as text."""
        lines = [
            "📊 Comparison Report",
            "=" * 50,
            "",
            f"Period 1: {data['period1']['range']}",
            str(data['period1']['summary']),
            "",
            f"Period 2: {data['period2']['range']}",
            str(data['period2']['summary']),
            "",
            "📈 Changes:",
            "-" * 20,
            f"Income Change: ${data['changes']['income_change']:+.2f} ({data['changes']['income_pct_change']:+.1f}%)",
            f"Expense Change: ${data['changes']['expense_change']:+.2f} ({data['changes']['expense_pct_change']:+.1f}%)",
            f"Net Change: ${data['changes']['net_change']:+.2f}",
        ]
        
        return "\n".join(lines)


# Global report generator instance
report_generator = ReportGenerator()

