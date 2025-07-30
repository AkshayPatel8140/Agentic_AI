"""
Database module for the Expense Tracker application.
Handles SQLite database operations and schema management.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class Database:
    """Database manager for the expense tracker."""
    
    def __init__(self, db_path: str = "expense_tracker.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            # Create categories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create transactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
                    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
                    category_id INTEGER,
                    description TEXT,
                    transaction_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id)")
            
            # Insert default categories
            self._insert_default_categories(conn)
            
            conn.commit()
    
    def _insert_default_categories(self, conn: sqlite3.Connection):
        """Insert default categories if they don't exist."""
        default_categories = [
            # Expense categories
            ('Food & Dining', 'expense'),
            ('Transportation', 'expense'),
            ('Shopping', 'expense'),
            ('Entertainment', 'expense'),
            ('Bills & Utilities', 'expense'),
            ('Healthcare', 'expense'),
            ('Education', 'expense'),
            ('Travel', 'expense'),
            ('Personal Care', 'expense'),
            ('Other Expenses', 'expense'),
            
            # Income categories
            ('Salary', 'income'),
            ('Freelance', 'income'),
            ('Business', 'income'),
            ('Investment', 'income'),
            ('Gift', 'income'),
            ('Other Income', 'income'),
        ]
        
        for name, category_type in default_categories:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
                    (name, category_type)
                )
            except sqlite3.IntegrityError:
                pass  # Category already exists
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE query and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def get_categories(self, category_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all categories, optionally filtered by type."""
        query = "SELECT * FROM categories"
        params = ()
        
        if category_type:
            query += " WHERE type = ?"
            params = (category_type,)
        
        query += " ORDER BY name"
        
        rows = self.execute_query(query, params)
        return [dict(row) for row in rows]
    
    def add_category(self, name: str, category_type: str) -> int:
        """Add a new category."""
        query = "INSERT INTO categories (name, type) VALUES (?, ?)"
        return self.execute_insert(query, (name, category_type))
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category if it's not being used."""
        # Check if category is being used
        usage_check = self.execute_query(
            "SELECT COUNT(*) as count FROM transactions WHERE category_id = ?",
            (category_id,)
        )
        
        if usage_check[0]['count'] > 0:
            return False  # Category is being used
        
        affected_rows = self.execute_update(
            "DELETE FROM categories WHERE id = ?",
            (category_id,)
        )
        return affected_rows > 0
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database."""
        with self.get_connection() as conn:
            with open(backup_path, 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        
        # Get transaction counts
        transaction_stats = self.execute_query("""
            SELECT 
                type,
                COUNT(*) as count,
                SUM(amount) as total,
                AVG(amount) as average
            FROM transactions 
            GROUP BY type
        """)
        
        for row in transaction_stats:
            stats[f"{row['type']}_count"] = row['count']
            stats[f"{row['type']}_total"] = float(row['total']) if row['total'] else 0
            stats[f"{row['type']}_average"] = float(row['average']) if row['average'] else 0
        
        # Get category counts
        category_stats = self.execute_query("""
            SELECT type, COUNT(*) as count 
            FROM categories 
            GROUP BY type
        """)
        
        for row in category_stats:
            stats[f"{row['type']}_categories"] = row['count']
        
        return stats


# Global database instance
db = Database()

