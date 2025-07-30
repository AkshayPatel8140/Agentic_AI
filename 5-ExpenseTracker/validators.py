"""
Validation utilities for the Expense Tracker application.
"""

import re
from typing import Tuple, Optional
from datetime import date
from .date_utils import DateUtils


class Validators:
    """Collection of validation functions."""
    
    @staticmethod
    def validate_amount(amount_str: str) -> Tuple[bool, Optional[float], str]:
        """
        Validate and parse a monetary amount.
        Returns (is_valid, parsed_amount, error_message).
        """
        if not amount_str:
            return False, None, "Amount is required"
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$€£¥₹,\s]', '', amount_str.strip())
        
        if not cleaned:
            return False, None, "Amount cannot be empty"
        
        try:
            amount = float(cleaned)
        except ValueError:
            return False, None, "Invalid amount format. Please enter a valid number."
        
        if amount <= 0:
            return False, None, "Amount must be greater than zero"
        
        if amount > 1000000:  # 1 million limit
            return False, None, "Amount cannot exceed $1,000,000"
        
        # Round to 2 decimal places
        amount = round(amount, 2)
        
        return True, amount, ""
    
    @staticmethod
    def validate_transaction_type(transaction_type: str) -> Tuple[bool, str]:
        """
        Validate transaction type.
        Returns (is_valid, error_message).
        """
        if not transaction_type:
            return False, "Transaction type is required"
        
        transaction_type = transaction_type.strip().lower()
        
        if transaction_type not in ['expense', 'income']:
            return False, "Transaction type must be 'expense' or 'income'"
        
        return True, ""
    
    @staticmethod
    def validate_description(description: str, max_length: int = 255) -> Tuple[bool, str]:
        """
        Validate transaction description.
        Returns (is_valid, error_message).
        """
        if description and len(description) > max_length:
            return False, f"Description cannot exceed {max_length} characters"
        
        # Check for potentially harmful content (basic XSS prevention)
        if description and any(char in description for char in ['<', '>', '"', "'"]):
            return False, "Description contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_category_name(name: str) -> Tuple[bool, str]:
        """
        Validate category name.
        Returns (is_valid, error_message).
        """
        if not name:
            return False, "Category name is required"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Category name must be at least 2 characters long"
        
        if len(name) > 50:
            return False, "Category name cannot exceed 50 characters"
        
        # Check for valid characters (letters, numbers, spaces, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9\s\-_&]+$', name):
            return False, "Category name contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_date_input(date_input: str, allow_future: bool = False) -> Tuple[bool, Optional[date], str]:
        """
        Validate and parse date input.
        Returns (is_valid, parsed_date, error_message).
        """
        if not date_input:
            return False, None, "Date is required"
        
        parsed_date = DateUtils.parse_date(date_input)
        if not parsed_date:
            return False, None, "Invalid date format. Try formats like 'YYYY-MM-DD', 'today', 'yesterday', or '3 days ago'"
        
        is_valid, error_msg = DateUtils.validate_date(parsed_date, allow_future)
        if not is_valid:
            return False, None, error_msg
        
        return True, parsed_date, ""
    
    @staticmethod
    def validate_id(id_str: str, field_name: str = "ID") -> Tuple[bool, Optional[int], str]:
        """
        Validate and parse an ID field.
        Returns (is_valid, parsed_id, error_message).
        """
        if not id_str:
            return False, None, f"{field_name} is required"
        
        try:
            parsed_id = int(id_str)
        except ValueError:
            return False, None, f"{field_name} must be a valid number"
        
        if parsed_id <= 0:
            return False, None, f"{field_name} must be greater than zero"
        
        return True, parsed_id, ""
    
    @staticmethod
    def validate_date_range(start_date_str: str, end_date_str: str) -> Tuple[bool, Optional[date], Optional[date], str]:
        """
        Validate a date range.
        Returns (is_valid, start_date, end_date, error_message).
        """
        # Validate start date
        is_valid_start, start_date, start_error = Validators.validate_date_input(start_date_str, allow_future=True)
        if not is_valid_start:
            return False, None, None, f"Start date error: {start_error}"
        
        # Validate end date
        is_valid_end, end_date, end_error = Validators.validate_date_input(end_date_str, allow_future=True)
        if not is_valid_end:
            return False, None, None, f"End date error: {end_error}"
        
        # Check if start date is before end date
        if start_date > end_date:
            return False, None, None, "Start date must be before or equal to end date"
        
        return True, start_date, end_date, ""
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitize user input by removing potentially harmful characters.
        """
        if not input_str:
            return ""
        
        # Remove or escape potentially harmful characters
        sanitized = input_str.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Limit length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, str]:
        """
        Validate search query.
        Returns (is_valid, error_message).
        """
        if not query:
            return False, "Search query cannot be empty"
        
        query = query.strip()
        
        if len(query) < 2:
            return False, "Search query must be at least 2 characters long"
        
        if len(query) > 100:
            return False, "Search query cannot exceed 100 characters"
        
        return True, ""
    
    @staticmethod
    def validate_limit(limit_str: str, max_limit: int = 1000) -> Tuple[bool, Optional[int], str]:
        """
        Validate a limit parameter.
        Returns (is_valid, parsed_limit, error_message).
        """
        if not limit_str:
            return True, None, ""  # Limit is optional
        
        try:
            limit = int(limit_str)
        except ValueError:
            return False, None, "Limit must be a valid number"
        
        if limit <= 0:
            return False, None, "Limit must be greater than zero"
        
        if limit > max_limit:
            return False, None, f"Limit cannot exceed {max_limit}"
        
        return True, limit, ""

