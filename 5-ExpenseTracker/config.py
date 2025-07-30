"""
Configuration settings for the Expense Tracker application.
"""

import os
from pathlib import Path


class Config:
    """Application configuration."""
    
    # Database settings
    DATABASE_PATH = os.getenv('EXPENSE_TRACKER_DB', 'expense_tracker.db')
    
    # Application settings
    APP_NAME = "Daily Expense & Income Tracker"
    APP_VERSION = "1.0.0"
    
    # Date settings
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"
    DISPLAY_DATE_FORMAT = "%B %d, %Y"
    
    # Validation limits
    MAX_AMOUNT = 1000000.0  # $1 million
    MAX_DESCRIPTION_LENGTH = 255
    MAX_CATEGORY_NAME_LENGTH = 50
    MAX_SEARCH_QUERY_LENGTH = 100
    MAX_TRANSACTIONS_PER_QUERY = 1000
    
    # Report settings
    DEFAULT_REPORT_LIMIT = 50
    MAX_REPORT_TRANSACTIONS = 1000
    
    # Backup settings
    AUTO_BACKUP = os.getenv('EXPENSE_TRACKER_AUTO_BACKUP', 'false').lower() == 'true'
    BACKUP_DIRECTORY = os.getenv('EXPENSE_TRACKER_BACKUP_DIR', 'backups')
    MAX_BACKUP_FILES = 10
    
    # Display settings
    CURRENCY_SYMBOL = "$"
    DECIMAL_PLACES = 2
    
    # CLI settings
    CLI_PAGE_SIZE = 20
    CLI_MAX_DESCRIPTION_DISPLAY = 50
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get the full path to the database file."""
        if os.path.isabs(cls.DATABASE_PATH):
            return cls.DATABASE_PATH
        
        # If relative path, make it relative to the application directory
        app_dir = Path(__file__).parent
        return str(app_dir / cls.DATABASE_PATH)
    
    @classmethod
    def get_backup_directory(cls) -> str:
        """Get the full path to the backup directory."""
        if os.path.isabs(cls.BACKUP_DIRECTORY):
            return cls.BACKUP_DIRECTORY
        
        # If relative path, make it relative to the application directory
        app_dir = Path(__file__).parent
        backup_dir = app_dir / cls.BACKUP_DIRECTORY
        backup_dir.mkdir(exist_ok=True)
        return str(backup_dir)
    
    @classmethod
    def format_currency(cls, amount: float) -> str:
        """Format an amount as currency."""
        return f"{cls.CURRENCY_SYMBOL}{amount:.{cls.DECIMAL_PLACES}f}"
    
    @classmethod
    def get_default_categories(cls) -> dict:
        """Get default categories for initialization."""
        return {
            'expense': [
                'Food & Dining',
                'Transportation',
                'Shopping',
                'Entertainment',
                'Bills & Utilities',
                'Healthcare',
                'Education',
                'Travel',
                'Personal Care',
                'Other Expenses'
            ],
            'income': [
                'Salary',
                'Freelance',
                'Business',
                'Investment',
                'Gift',
                'Other Income'
            ]
        }


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_PATH = 'expense_tracker_dev.db'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    AUTO_BACKUP = True


class TestConfig(Config):
    """Test configuration."""
    DEBUG = True
    DATABASE_PATH = ':memory:'  # In-memory database for tests
    AUTO_BACKUP = False


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': Config
}


def get_config(config_name: str = None) -> Config:
    """Get configuration based on environment."""
    if config_name is None:
        config_name = os.getenv('EXPENSE_TRACKER_ENV', 'default')
    
    return config_map.get(config_name, Config)

