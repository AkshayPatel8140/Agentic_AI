"""
Tests for the database module.
"""

import unittest
import tempfile
import os
from datetime import date
from ..database import Database


class TestDatabase(unittest.TestCase):
    """Test cases for the Database class."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test that database initializes correctly."""
        # Check that tables exist
        tables = self.db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [row['name'] for row in tables]
        
        self.assertIn('categories', table_names)
        self.assertIn('transactions', table_names)
    
    def test_default_categories_created(self):
        """Test that default categories are created."""
        categories = self.db.get_categories()
        
        # Should have both expense and income categories
        expense_categories = [c for c in categories if c['type'] == 'expense']
        income_categories = [c for c in categories if c['type'] == 'income']
        
        self.assertGreater(len(expense_categories), 0)
        self.assertGreater(len(income_categories), 0)
        
        # Check for some expected categories
        category_names = [c['name'] for c in categories]
        self.assertIn('Food & Dining', category_names)
        self.assertIn('Salary', category_names)
    
    def test_add_category(self):
        """Test adding a new category."""
        category_id = self.db.add_category('Test Category', 'expense')
        self.assertIsInstance(category_id, int)
        self.assertGreater(category_id, 0)
        
        # Verify category was added
        categories = self.db.get_categories('expense')
        category_names = [c['name'] for c in categories]
        self.assertIn('Test Category', category_names)
    
    def test_get_categories_filtered(self):
        """Test getting categories filtered by type."""
        expense_categories = self.db.get_categories('expense')
        income_categories = self.db.get_categories('income')
        
        # All expense categories should have type 'expense'
        for category in expense_categories:
            self.assertEqual(category['type'], 'expense')
        
        # All income categories should have type 'income'
        for category in income_categories:
            self.assertEqual(category['type'], 'income')
    
    def test_database_stats(self):
        """Test getting database statistics."""
        stats = self.db.get_database_stats()
        
        # Should have category counts
        self.assertIn('expense_categories', stats)
        self.assertIn('income_categories', stats)
        
        # Should have transaction counts (initially 0)
        self.assertEqual(stats.get('expense_count', 0), 0)
        self.assertEqual(stats.get('income_count', 0), 0)


if __name__ == '__main__':
    unittest.main()

