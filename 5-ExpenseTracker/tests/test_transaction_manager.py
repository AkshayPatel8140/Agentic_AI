"""
Tests for the transaction manager module.
"""

import unittest
import tempfile
import os
from datetime import date, timedelta
from ..database import Database
from ..transaction_manager import TransactionManager


class TestTransactionManager(unittest.TestCase):
    """Test cases for the TransactionManager class."""
    
    def setUp(self):
        """Set up test database and transaction manager."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create database instance
        self.db = Database(self.temp_db.name)
        
        # Create transaction manager with test database
        self.tm = TransactionManager()
        self.tm.db = self.db
        
        # Get a test category
        categories = self.db.get_categories('expense')
        self.test_category_id = categories[0]['id'] if categories else None
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_add_transaction_success(self):
        """Test successfully adding a transaction."""
        success, transaction_id, message = self.tm.add_transaction(
            transaction_type='expense',
            amount=25.50,
            category_id=self.test_category_id,
            description='Test expense',
            transaction_date=date.today()
        )
        
        self.assertTrue(success)
        self.assertIsInstance(transaction_id, int)
        self.assertGreater(transaction_id, 0)
        self.assertIn('successfully', message.lower())
    
    def test_add_transaction_invalid_type(self):
        """Test adding transaction with invalid type."""
        success, transaction_id, message = self.tm.add_transaction(
            transaction_type='invalid',
            amount=25.50,
            category_id=self.test_category_id,
            description='Test expense',
            transaction_date=date.today()
        )
        
        self.assertFalse(success)
        self.assertIsNone(transaction_id)
        self.assertIn('invalid', message.lower())
    
    def test_add_transaction_invalid_amount(self):
        """Test adding transaction with invalid amount."""
        success, transaction_id, message = self.tm.add_transaction(
            transaction_type='expense',
            amount=-10.0,
            category_id=self.test_category_id,
            description='Test expense',
            transaction_date=date.today()
        )
        
        self.assertFalse(success)
        self.assertIsNone(transaction_id)
        self.assertIn('amount', message.lower())
    
    def test_get_transaction_by_id(self):
        """Test retrieving a transaction by ID."""
        # Add a transaction first
        success, transaction_id, _ = self.tm.add_transaction(
            transaction_type='income',
            amount=100.0,
            category_id=None,
            description='Test income',
            transaction_date=date.today()
        )
        
        self.assertTrue(success)
        
        # Retrieve the transaction
        transaction = self.tm.get_transaction_by_id(transaction_id)
        
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.id, transaction_id)
        self.assertEqual(transaction.type, 'income')
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.description, 'Test income')
    
    def test_update_transaction(self):
        """Test updating a transaction."""
        # Add a transaction first
        success, transaction_id, _ = self.tm.add_transaction(
            transaction_type='expense',
            amount=50.0,
            category_id=self.test_category_id,
            description='Original description',
            transaction_date=date.today()
        )
        
        self.assertTrue(success)
        
        # Update the transaction
        success, message = self.tm.update_transaction(
            transaction_id=transaction_id,
            amount=75.0,
            description='Updated description'
        )
        
        self.assertTrue(success)
        self.assertIn('updated', message.lower())
        
        # Verify the update
        updated_transaction = self.tm.get_transaction_by_id(transaction_id)
        self.assertEqual(updated_transaction.amount, 75.0)
        self.assertEqual(updated_transaction.description, 'Updated description')
    
    def test_delete_transaction(self):
        """Test deleting a transaction."""
        # Add a transaction first
        success, transaction_id, _ = self.tm.add_transaction(
            transaction_type='expense',
            amount=30.0,
            category_id=self.test_category_id,
            description='To be deleted',
            transaction_date=date.today()
        )
        
        self.assertTrue(success)
        
        # Delete the transaction
        success, message = self.tm.delete_transaction(transaction_id)
        
        self.assertTrue(success)
        self.assertIn('deleted', message.lower())
        
        # Verify deletion
        deleted_transaction = self.tm.get_transaction_by_id(transaction_id)
        self.assertIsNone(deleted_transaction)
    
    def test_get_transactions_by_date(self):
        """Test getting transactions for a specific date."""
        test_date = date.today()
        
        # Add transactions for today
        self.tm.add_transaction('expense', 20.0, self.test_category_id, 'Expense 1', test_date)
        self.tm.add_transaction('income', 100.0, None, 'Income 1', test_date)
        
        # Add transaction for yesterday
        yesterday = test_date - timedelta(days=1)
        self.tm.add_transaction('expense', 15.0, self.test_category_id, 'Yesterday expense', yesterday)
        
        # Get today's transactions
        today_transactions = self.tm.get_transactions_by_date(test_date)
        
        self.assertEqual(len(today_transactions), 2)
        for transaction in today_transactions:
            self.assertEqual(transaction.transaction_date, test_date)
    
    def test_get_transaction_summary(self):
        """Test getting transaction summary."""
        test_date = date.today()
        
        # Add some transactions
        self.tm.add_transaction('expense', 25.0, self.test_category_id, 'Expense 1', test_date)
        self.tm.add_transaction('expense', 15.0, self.test_category_id, 'Expense 2', test_date)
        self.tm.add_transaction('income', 100.0, None, 'Income 1', test_date)
        
        # Get summary
        summary = self.tm.get_transaction_summary(test_date, test_date)
        
        self.assertEqual(summary.total_expenses, 40.0)
        self.assertEqual(summary.total_income, 100.0)
        self.assertEqual(summary.net_balance, 60.0)
        self.assertEqual(summary.expense_count, 2)
        self.assertEqual(summary.income_count, 1)
        self.assertEqual(summary.transaction_count, 3)
    
    def test_search_transactions(self):
        """Test searching transactions."""
        # Add transactions with different descriptions
        self.tm.add_transaction('expense', 10.0, self.test_category_id, 'Coffee shop', date.today())
        self.tm.add_transaction('expense', 20.0, self.test_category_id, 'Restaurant dinner', date.today())
        self.tm.add_transaction('income', 50.0, None, 'Coffee sales', date.today())
        
        # Search for "coffee"
        results = self.tm.search_transactions('coffee')
        
        self.assertEqual(len(results), 2)  # Should find both coffee-related transactions
        
        descriptions = [t.description.lower() for t in results]
        self.assertTrue(all('coffee' in desc for desc in descriptions))
    
    def test_add_category(self):
        """Test adding a new category."""
        success, category_id, message = self.tm.add_category('Test Category', 'expense')
        
        self.assertTrue(success)
        self.assertIsInstance(category_id, int)
        self.assertGreater(category_id, 0)
        self.assertIn('successfully', message.lower())
        
        # Verify category was added
        category = self.tm.get_category_by_id(category_id)
        self.assertIsNotNone(category)
        self.assertEqual(category['name'], 'Test Category')
        self.assertEqual(category['type'], 'expense')
    
    def test_add_duplicate_category(self):
        """Test adding a duplicate category."""
        # Add first category
        success1, _, _ = self.tm.add_category('Duplicate Test', 'expense')
        self.assertTrue(success1)
        
        # Try to add duplicate
        success2, category_id2, message2 = self.tm.add_category('Duplicate Test', 'expense')
        
        self.assertFalse(success2)
        self.assertIsNone(category_id2)
        self.assertIn('already exists', message2.lower())


if __name__ == '__main__':
    unittest.main()

