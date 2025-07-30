# 💰 Daily Expense & Income Tracker

A comprehensive Python application for tracking daily expenses and income with support for retroactive entries, categorization, and detailed reporting.

## ✨ Features

### Core Functionality
- **Manual Entry**: Add expenses and income with detailed information
- **Retroactive Entries**: Add transactions for previous dates if you missed entering them
- **Categories**: Organize transactions with predefined and custom categories
- **Flexible Date Input**: Support for various date formats and relative dates
- **Search & Filter**: Find transactions by description, category, or date range

### Reporting & Analytics
- **Daily Reports**: View transactions and summary for any specific day
- **Weekly/Monthly/Yearly Reports**: Comprehensive period-based analysis
- **Category Analysis**: Track spending patterns by category
- **Comparison Reports**: Compare different time periods
- **Summary Statistics**: Quick overview of financial status

### User Interface
- **Web Interface**: Modern, responsive web application with Bootstrap UI
- **Interactive Terminal Mode**: User-friendly menu-driven interface
- **Command Line Interface**: Full CLI support for power users
- **Data Validation**: Comprehensive input validation and error handling

## 🚀 Quick Start

### Web Application (Recommended)
```bash
cd 5-ExpenseTracker
pip install Flask>=2.3.0
python run_web.py
```
Then open your browser to `http://localhost:5000`

### Interactive Terminal Mode
```bash
cd 5-ExpenseTracker
python main.py
```

### Command Line Mode
```bash
# Add an expense
python main.py add expense 25.50 --category 1 --description "Lunch" --date today

# Add income
python main.py add income 1000 --category 11 --description "Salary" --date yesterday

# View today's transactions
python main.py list --date today

# Generate monthly report
python main.py report monthly

# View all categories
python main.py categories list
```

## 📋 Usage Examples

### Adding Transactions

**Interactive Mode:**
1. Run `python main.py`
2. Choose option 1 (Add expense) or 2 (Add income)
3. Follow the prompts to enter amount, category, description, and date

**Command Line:**
```bash
# Add expense with category
python main.py add expense 15.75 --category 1 --description "Coffee and pastry" --date today

# Add income for a previous date
python main.py add income 500 --category 11 --description "Freelance payment" --date "2023-12-01"

# Add transaction without category
python main.py add expense 50 --description "Miscellaneous expense" --date yesterday
```

### Viewing Transactions

```bash
# View today's transactions
python main.py list --date today

# View transactions for a specific date
python main.py list --date "2023-12-01"

# View transactions for a date range
python main.py list --date "this week"
python main.py list --date "2023-12-01 to 2023-12-31"

# Filter by transaction type
python main.py list --type expense --date "this month"

# Search transactions
python main.py search "coffee"
```

### Generating Reports

```bash
# Daily report for today
python main.py report daily

# Weekly report for current week
python main.py report weekly

# Monthly report for a specific month
python main.py report monthly --date "2023-12-15"

# Category report
python main.py report category --category 1 --start "2023-12-01" --end "2023-12-31"

# Comparison report
python main.py report comparison --start "2023-11-01" --end "2023-11-30" --compare-start "2023-12-01" --compare-end "2023-12-31"
```

### Managing Categories

```bash
# List all categories
python main.py categories list

# Add new category
python main.py categories add "Gym Membership" expense

# Delete category (only if not used)
python main.py categories delete 15 --confirm
```

## 📅 Supported Date Formats

### Absolute Dates
- `2023-12-25` (YYYY-MM-DD)
- `25/12/2023` (DD/MM/YYYY)
- `12/25/2023` (MM/DD/YYYY)
- `25-12-2023` (DD-MM-YYYY)
- `25.12.2023` (DD.MM.YYYY)

### Relative Dates
- `today`, `now`
- `yesterday`
- `tomorrow`
- `3 days ago`
- `last week`
- `last month`

### Date Ranges
- `this week`, `this month`, `this year`
- `last week`, `last month`, `last year`
- `2023-01-01 to 2023-01-31`
- `01/01/2023 - 01/31/2023`

## 📊 Default Categories

### Expense Categories
- Food & Dining
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Education
- Travel
- Personal Care
- Other Expenses

### Income Categories
- Salary
- Freelance
- Business
- Investment
- Gift
- Other Income

## 🗄️ Database Schema

The application uses SQLite with the following structure:

### Categories Table
- `id`: Primary key
- `name`: Category name (unique)
- `type`: 'expense' or 'income'
- `created_at`: Timestamp

### Transactions Table
- `id`: Primary key
- `type`: 'expense' or 'income'
- `amount`: Decimal amount (must be positive)
- `category_id`: Foreign key to categories
- `description`: Optional description
- `transaction_date`: Date of transaction
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

## 🔧 Configuration

The application can be configured through environment variables:

```bash
# Database location
export EXPENSE_TRACKER_DB="/path/to/your/database.db"

# Environment (development, production, test)
export EXPENSE_TRACKER_ENV="production"

# Enable automatic backups
export EXPENSE_TRACKER_AUTO_BACKUP="true"

# Backup directory
export EXPENSE_TRACKER_BACKUP_DIR="/path/to/backups"
```

## 📁 Project Structure

```
5-ExpenseTracker/
├── __init__.py              # Package initialization
├── main.py                  # Terminal/CLI entry point
├── run_web.py              # Web application startup script
├── web_app.py              # Flask web application
├── cli.py                   # Command-line interface
├── database.py              # Database operations
├── models.py                # Data models
├── transaction_manager.py   # Transaction CRUD operations
├── reports.py               # Report generation
├── date_utils.py           # Date parsing and utilities
├── validators.py           # Input validation
├── config.py               # Configuration management
├── requirements.txt        # Dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── add_transaction.html
│   ├── transactions.html
│   ├── reports.html
│   └── categories.html
├── static/               # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── tests/                 # Test files
    ├── test_database.py
    ├── test_transaction_manager.py
    └── ...
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=5-ExpenseTracker

# Run specific test file
python -m pytest tests/test_transaction_manager.py
```

## 🔒 Data Security

- All data is stored locally in SQLite database
- Input validation prevents SQL injection
- No sensitive data is logged
- Automatic backup functionality available

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues, questions, or feature requests, please create an issue in the repository.

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - Transaction management (add, update, delete, view)
  - Category management
  - Flexible date handling
  - Comprehensive reporting
  - CLI and interactive interfaces
  - Data validation and error handling

## 🎯 Future Enhancements

- Web interface using Flask/FastAPI
- Data export to CSV/Excel
- Data visualization with charts
- Budget tracking and alerts
- Multi-currency support
- Cloud synchronization
- Mobile app companion
