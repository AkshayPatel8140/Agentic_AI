"""
Data models for the Expense Tracker application.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, Any


@dataclass
class Category:
    """Represents a transaction category."""
    id: int
    name: str
    type: str  # 'expense' or 'income'
    created_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """Create a Category instance from a dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            type=data['type'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class Transaction:
    """Represents a financial transaction."""
    id: Optional[int]
    type: str  # 'expense' or 'income'
    amount: float
    category_id: Optional[int]
    description: Optional[str]
    transaction_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category_name: Optional[str] = None  # For display purposes
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create a Transaction instance from a dictionary."""
        return cls(
            id=data.get('id'),
            type=data['type'],
            amount=float(data['amount']),
            category_id=data.get('category_id'),
            description=data.get('description'),
            transaction_date=date.fromisoformat(data['transaction_date']) if isinstance(data['transaction_date'], str) else data['transaction_date'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') and isinstance(data['created_at'], str) else data.get('created_at'),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') and isinstance(data['updated_at'], str) else data.get('updated_at'),
            category_name=data.get('category_name')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Transaction to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'category_id': self.category_id,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category_name': self.category_name
        }
    
    def __str__(self) -> str:
        """String representation of the transaction."""
        symbol = "-" if self.type == "expense" else "+"
        category = f" ({self.category_name})" if self.category_name else ""
        description = f" - {self.description}" if self.description else ""
        return f"{self.transaction_date} | {symbol}${self.amount:.2f}{category}{description}"


@dataclass
class TransactionSummary:
    """Represents a summary of transactions."""
    total_income: float = 0.0
    total_expenses: float = 0.0
    net_balance: float = 0.0
    transaction_count: int = 0
    income_count: int = 0
    expense_count: int = 0
    date_range: Optional[str] = None
    
    @property
    def net_balance(self) -> float:
        """Calculate net balance."""
        return self.total_income - self.total_expenses
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary."""
        return {
            'total_income': self.total_income,
            'total_expenses': self.total_expenses,
            'net_balance': self.net_balance,
            'transaction_count': self.transaction_count,
            'income_count': self.income_count,
            'expense_count': self.expense_count,
            'date_range': self.date_range
        }
    
    def __str__(self) -> str:
        """String representation of the summary."""
        lines = []
        if self.date_range:
            lines.append(f"Summary for: {self.date_range}")
        lines.extend([
            f"Total Income: +${self.total_income:.2f} ({self.income_count} transactions)",
            f"Total Expenses: -${self.total_expenses:.2f} ({self.expense_count} transactions)",
            f"Net Balance: ${self.net_balance:+.2f}",
            f"Total Transactions: {self.transaction_count}"
        ])
        return "\n".join(lines)


@dataclass
class CategorySummary:
    """Represents a summary by category."""
    category_name: str
    category_type: str
    total_amount: float
    transaction_count: int
    average_amount: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category summary to dictionary."""
        return {
            'category_name': self.category_name,
            'category_type': self.category_type,
            'total_amount': self.total_amount,
            'transaction_count': self.transaction_count,
            'average_amount': self.average_amount
        }
    
    def __str__(self) -> str:
        """String representation of the category summary."""
        symbol = "-" if self.category_type == "expense" else "+"
        return f"{self.category_name}: {symbol}${self.total_amount:.2f} ({self.transaction_count} transactions, avg: ${self.average_amount:.2f})"

