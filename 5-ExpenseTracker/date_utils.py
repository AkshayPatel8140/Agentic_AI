"""
Date utilities for the Expense Tracker application.
Handles date parsing, validation, and formatting.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple
import re


class DateUtils:
    """Utility class for date operations."""
    
    # Common date formats to try
    DATE_FORMATS = [
        "%Y-%m-%d",      # 2023-12-25
        "%d/%m/%Y",      # 25/12/2023
        "%m/%d/%Y",      # 12/25/2023
        "%d-%m-%Y",      # 25-12-2023
        "%m-%d-%Y",      # 12-25-2023
        "%d.%m.%Y",      # 25.12.2023
        "%Y/%m/%d",      # 2023/12/25
    ]
    
    @staticmethod
    def parse_date(date_input: str) -> Optional[date]:
        """
        Parse a date string into a date object.
        Supports various formats and relative dates.
        """
        if not date_input:
            return None
        
        date_input = date_input.strip().lower()
        
        # Handle relative dates
        if date_input in ['today', 'now']:
            return date.today()
        elif date_input == 'yesterday':
            return date.today() - timedelta(days=1)
        elif date_input == 'tomorrow':
            return date.today() + timedelta(days=1)
        
        # Handle "X days ago" format
        days_ago_match = re.match(r'(\d+)\s*days?\s*ago', date_input)
        if days_ago_match:
            days = int(days_ago_match.group(1))
            return date.today() - timedelta(days=days)
        
        # Handle "last week", "last month" etc.
        if date_input == 'last week':
            return date.today() - timedelta(weeks=1)
        elif date_input == 'last month':
            today = date.today()
            if today.month == 1:
                return date(today.year - 1, 12, today.day)
            else:
                try:
                    return date(today.year, today.month - 1, today.day)
                except ValueError:
                    # Handle cases like March 31 -> February (no 31st)
                    return date(today.year, today.month - 1, 28)
        
        # Try parsing with different formats
        for fmt in DateUtils.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_input, fmt).date()
                return parsed_date
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def validate_date(target_date: date, allow_future: bool = False) -> Tuple[bool, str]:
        """
        Validate a date.
        Returns (is_valid, error_message).
        """
        if not target_date:
            return False, "Invalid date format"
        
        today = date.today()
        
        # Check if date is too far in the past (more than 10 years)
        ten_years_ago = today - timedelta(days=365 * 10)
        if target_date < ten_years_ago:
            return False, f"Date cannot be more than 10 years ago ({ten_years_ago})"
        
        # Check if date is in the future (unless allowed)
        if not allow_future and target_date > today:
            return False, "Date cannot be in the future"
        
        # Check if date is too far in the future (more than 1 year)
        if allow_future and target_date > today + timedelta(days=365):
            return False, "Date cannot be more than 1 year in the future"
        
        return True, ""
    
    @staticmethod
    def format_date(target_date: date, format_type: str = "default") -> str:
        """
        Format a date for display.
        
        Args:
            target_date: The date to format
            format_type: Type of formatting ('default', 'short', 'long', 'relative')
        """
        if not target_date:
            return "N/A"
        
        if format_type == "short":
            return target_date.strftime("%m/%d/%y")
        elif format_type == "long":
            return target_date.strftime("%A, %B %d, %Y")
        elif format_type == "relative":
            return DateUtils.get_relative_date_string(target_date)
        else:  # default
            return target_date.strftime("%Y-%m-%d")
    
    @staticmethod
    def get_relative_date_string(target_date: date) -> str:
        """Get a relative date string (e.g., 'today', 'yesterday', '3 days ago')."""
        if not target_date:
            return "N/A"
        
        today = date.today()
        diff = (today - target_date).days
        
        if diff == 0:
            return "today"
        elif diff == 1:
            return "yesterday"
        elif diff == -1:
            return "tomorrow"
        elif diff > 1:
            if diff < 7:
                return f"{diff} days ago"
            elif diff < 30:
                weeks = diff // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif diff < 365:
                months = diff // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = diff // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
        else:  # future dates
            diff = abs(diff)
            if diff < 7:
                return f"in {diff} days"
            elif diff < 30:
                weeks = diff // 7
                return f"in {weeks} week{'s' if weeks > 1 else ''}"
            else:
                months = diff // 30
                return f"in {months} month{'s' if months > 1 else ''}"
    
    @staticmethod
    def get_date_range(start_date: date, end_date: date) -> Tuple[date, date]:
        """
        Ensure start_date is before end_date.
        Returns (start_date, end_date) in correct order.
        """
        if start_date > end_date:
            return end_date, start_date
        return start_date, end_date
    
    @staticmethod
    def get_week_range(target_date: date = None) -> Tuple[date, date]:
        """Get the start and end dates of the week containing the target date."""
        if target_date is None:
            target_date = date.today()
        
        # Monday is 0, Sunday is 6
        days_since_monday = target_date.weekday()
        start_of_week = target_date - timedelta(days=days_since_monday)
        end_of_week = start_of_week + timedelta(days=6)
        
        return start_of_week, end_of_week
    
    @staticmethod
    def get_month_range(target_date: date = None) -> Tuple[date, date]:
        """Get the start and end dates of the month containing the target date."""
        if target_date is None:
            target_date = date.today()
        
        start_of_month = date(target_date.year, target_date.month, 1)
        
        # Get the last day of the month
        if target_date.month == 12:
            next_month = date(target_date.year + 1, 1, 1)
        else:
            next_month = date(target_date.year, target_date.month + 1, 1)
        
        end_of_month = next_month - timedelta(days=1)
        
        return start_of_month, end_of_month
    
    @staticmethod
    def get_year_range(target_date: date = None) -> Tuple[date, date]:
        """Get the start and end dates of the year containing the target date."""
        if target_date is None:
            target_date = date.today()
        
        start_of_year = date(target_date.year, 1, 1)
        end_of_year = date(target_date.year, 12, 31)
        
        return start_of_year, end_of_year
    
    @staticmethod
    def parse_date_range(range_input: str) -> Optional[Tuple[date, date]]:
        """
        Parse a date range string.
        Supports formats like:
        - "2023-01-01 to 2023-01-31"
        - "01/01/2023 - 01/31/2023"
        - "this week", "this month", "this year"
        - "last week", "last month", "last year"
        """
        if not range_input:
            return None
        
        range_input = range_input.strip().lower()
        
        # Handle predefined ranges
        if range_input == "this week":
            return DateUtils.get_week_range()
        elif range_input == "this month":
            return DateUtils.get_month_range()
        elif range_input == "this year":
            return DateUtils.get_year_range()
        elif range_input == "last week":
            last_week = date.today() - timedelta(weeks=1)
            return DateUtils.get_week_range(last_week)
        elif range_input == "last month":
            today = date.today()
            if today.month == 1:
                last_month = date(today.year - 1, 12, 15)
            else:
                last_month = date(today.year, today.month - 1, 15)
            return DateUtils.get_month_range(last_month)
        elif range_input == "last year":
            last_year = date(date.today().year - 1, 6, 15)
            return DateUtils.get_year_range(last_year)
        
        # Handle explicit date ranges
        separators = [' to ', ' - ', ' -- ', '..', ' through ']
        for sep in separators:
            if sep in range_input:
                parts = range_input.split(sep, 1)
                if len(parts) == 2:
                    start_date = DateUtils.parse_date(parts[0].strip())
                    end_date = DateUtils.parse_date(parts[1].strip())
                    if start_date and end_date:
                        return DateUtils.get_date_range(start_date, end_date)
        
        return None

