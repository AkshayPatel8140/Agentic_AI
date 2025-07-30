"""
Transaction management module for the Expense Tracker application.
Handles all CRUD operations for transactions.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime
from .database import db
from .models import Transaction, TransactionSummary, CategorySummary
from .validators import Validators
from .date_utils import DateUtils


class TransactionManager:
    """Manages all transaction operations."""
    
    def __init__(self):
        self.db = db
    
    def add_transaction(
        self,
        transaction_type: str,
        amount: float,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        transaction_date: Optional[date] = None
    ) -> Tuple[bool, Optional[int], str]:
        """
        Add a new transaction.
        Returns (success, transaction_id, message).
        """
        # Use today's date if not provided
        if transaction_date is None:
            transaction_date = date.today()
        
        # Validate inputs
        if not Validators.validate_transaction_type(transaction_type)[0]:
            return False, None, "Invalid transaction type"
        
        if amount <= 0:
            return False, None, "Amount must be greater than zero"
        
        if description:
            is_valid, error_msg = Validators.validate_description(description)
            if not is_valid:
                return False, None, error_msg
        
        # Validate category exists if provided
        if category_id:
            category = self.get_category_by_id(category_id)
            if not category:
                return False, None, "Category not found"
            
            # Check if category type matches transaction type
            if category['type'] != transaction_type:
                return False, None, f"Category type ({category['type']}) doesn't match transaction type ({transaction_type})"
        
        try:
            query = """
                INSERT INTO transactions (type, amount, category_id, description, transaction_date)
                VALUES (?, ?, ?, ?, ?)
            """
            transaction_id = self.db.execute_insert(
                query,
                (transaction_type, amount, category_id, description, transaction_date.isoformat())
            )
            
            return True, transaction_id, "Transaction added successfully"
        
        except Exception as e:
            return False, None, f"Error adding transaction: {str(e)}"
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by its ID."""
        query = """
            SELECT t.*, c.name as category_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?
        """
        
        rows = self.db.execute_query(query, (transaction_id,))
        if rows:
            return Transaction.from_dict(dict(rows[0]))
        return None
    
    def update_transaction(
        self,
        transaction_id: int,
        transaction_type: Optional[str] = None,
        amount: Optional[float] = None,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        transaction_date: Optional[date] = None
    ) -> Tuple[bool, str]:
        """
        Update an existing transaction.
        Returns (success, message).
        """
        # Get existing transaction
        existing = self.get_transaction_by_id(transaction_id)
        if not existing:
            return False, "Transaction not found"
        
        # Prepare update data
        updates = []
        params = []
        
        if transaction_type is not None:
            if not Validators.validate_transaction_type(transaction_type)[0]:
                return False, "Invalid transaction type"
            updates.append("type = ?")
            params.append(transaction_type)
        
        if amount is not None:
            if amount <= 0:
                return False, "Amount must be greater than zero"
            updates.append("amount = ?")
            params.append(amount)
        
        if category_id is not None:
            if category_id > 0:  # Allow setting to None (0 or negative means remove category)
                category = self.get_category_by_id(category_id)
                if not category:
                    return False, "Category not found"
                
                # Check type compatibility
                check_type = transaction_type if transaction_type else existing.type
                if category['type'] != check_type:
                    return False, f"Category type doesn't match transaction type"
            
            updates.append("category_id = ?")
            params.append(category_id if category_id > 0 else None)
        
        if description is not None:
            is_valid, error_msg = Validators.validate_description(description)
            if not is_valid:
                return False, error_msg
            updates.append("description = ?")
            params.append(description)
        
        if transaction_date is not None:
            updates.append("transaction_date = ?")
            params.append(transaction_date.isoformat())
        
        if not updates:
            return False, "No updates provided"
        
        # Add updated_at timestamp
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add transaction ID for WHERE clause
        params.append(transaction_id)
        
        try:
            query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
            affected_rows = self.db.execute_update(query, tuple(params))
            
            if affected_rows > 0:
                return True, "Transaction updated successfully"
            else:
                return False, "Transaction not found"
        
        except Exception as e:
            return False, f"Error updating transaction: {str(e)}"
    
    def delete_transaction(self, transaction_id: int) -> Tuple[bool, str]:
        """
        Delete a transaction.
        Returns (success, message).
        """
        try:
            affected_rows = self.db.execute_update(
                "DELETE FROM transactions WHERE id = ?",
                (transaction_id,)
            )
            
            if affected_rows > 0:
                return True, "Transaction deleted successfully"
            else:
                return False, "Transaction not found"
        
        except Exception as e:
            return False, f"Error deleting transaction: {str(e)}"
    
    def get_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[str] = None,
        category_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "transaction_date DESC"
    ) -> List[Transaction]:
        """Get transactions with optional filtering."""
        query = """
            SELECT t.*, c.name as category_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if start_date:
            query += " AND t.transaction_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND t.transaction_date <= ?"
            params.append(end_date.isoformat())
        
        if transaction_type:
            query += " AND t.type = ?"
            params.append(transaction_type)
        
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        
        # Add ordering
        query += f" ORDER BY {order_by}"
        
        # Add limit and offset
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
            if offset > 0:
                query += " OFFSET ?"
                params.append(offset)
        
        rows = self.db.execute_query(query, tuple(params))
        return [Transaction.from_dict(dict(row)) for row in rows]
    
    def get_transactions_by_date(self, target_date: date) -> List[Transaction]:
        """Get all transactions for a specific date."""
        return self.get_transactions(
            start_date=target_date,
            end_date=target_date,
            order_by="created_at DESC"
        )
    
    def search_transactions(self, search_query: str, limit: int = 50) -> List[Transaction]:
        """Search transactions by description or category name."""
        query = """
            SELECT t.*, c.name as category_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.description LIKE ? OR c.name LIKE ?
            ORDER BY t.transaction_date DESC
            LIMIT ?
        """
        
        search_pattern = f"%{search_query}%"
        rows = self.db.execute_query(query, (search_pattern, search_pattern, limit))
        return [Transaction.from_dict(dict(row)) for row in rows]
    
    def get_transaction_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TransactionSummary:
        """Get a summary of transactions for a date range."""
        query = """
            SELECT 
                type,
                COUNT(*) as count,
                SUM(amount) as total
            FROM transactions
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date.isoformat())
        
        query += " GROUP BY type"
        
        rows = self.db.execute_query(query, tuple(params))
        
        summary = TransactionSummary()
        
        for row in rows:
            if row['type'] == 'income':
                summary.total_income = float(row['total'])
                summary.income_count = row['count']
            elif row['type'] == 'expense':
                summary.total_expenses = float(row['total'])
                summary.expense_count = row['count']
        
        summary.transaction_count = summary.income_count + summary.expense_count
        
        # Set date range string
        if start_date and end_date:
            if start_date == end_date:
                summary.date_range = DateUtils.format_date(start_date)
            else:
                summary.date_range = f"{DateUtils.format_date(start_date)} to {DateUtils.format_date(end_date)}"
        elif start_date:
            summary.date_range = f"From {DateUtils.format_date(start_date)}"
        elif end_date:
            summary.date_range = f"Until {DateUtils.format_date(end_date)}"
        else:
            summary.date_range = "All time"
        
        return summary
    
    def get_category_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[str] = None
    ) -> List[CategorySummary]:
        """Get summary by category."""
        query = """
            SELECT 
                c.name as category_name,
                c.type as category_type,
                COUNT(t.id) as transaction_count,
                SUM(t.amount) as total_amount,
                AVG(t.amount) as average_amount
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND t.transaction_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND t.transaction_date <= ?"
            params.append(end_date.isoformat())
        
        if transaction_type:
            query += " AND t.type = ?"
            params.append(transaction_type)
        
        query += " GROUP BY c.id, c.name, c.type ORDER BY total_amount DESC"
        
        rows = self.db.execute_query(query, tuple(params))
        
        return [
            CategorySummary(
                category_name=row['category_name'],
                category_type=row['category_type'],
                total_amount=float(row['total_amount']),
                transaction_count=row['transaction_count'],
                average_amount=float(row['average_amount'])
            )
            for row in rows
        ]
    
    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Get category by ID."""
        rows = self.db.execute_query(
            "SELECT * FROM categories WHERE id = ?",
            (category_id,)
        )
        return dict(rows[0]) if rows else None
    
    def get_categories(self, category_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all categories, optionally filtered by type."""
        return self.db.get_categories(category_type)
    
    def add_category(self, name: str, category_type: str) -> Tuple[bool, Optional[int], str]:
        """Add a new category."""
        # Validate inputs
        is_valid_name, name_error = Validators.validate_category_name(name)
        if not is_valid_name:
            return False, None, name_error
        
        is_valid_type, type_error = Validators.validate_transaction_type(category_type)
        if not is_valid_type:
            return False, None, type_error
        
        try:
            category_id = self.db.add_category(name, category_type)
            return True, category_id, "Category added successfully"
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return False, None, "Category name already exists"
            return False, None, f"Error adding category: {str(e)}"
    
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """Delete a category if it's not being used."""
        try:
            success = self.db.delete_category(category_id)
            if success:
                return True, "Category deleted successfully"
            else:
                return False, "Category is being used by transactions and cannot be deleted"
        except Exception as e:
            return False, f"Error deleting category: {str(e)}"


# Global transaction manager instance
transaction_manager = TransactionManager()

