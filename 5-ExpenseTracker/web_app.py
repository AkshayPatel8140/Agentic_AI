"""
Flask web application for the Daily Expense & Income Tracker.
Provides a modern web-based UI for the expense tracking system.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import date, datetime, timedelta
import json
from typing import Dict, Any, List
from transaction_manager import transaction_manager
from reports import report_generator
from validators import Validators
from date_utils import DateUtils

app = Flask(__name__)
app.secret_key = 'expense_tracker_secret_key_2024'  # Change this in production

# Initialize components
tm = transaction_manager
rg = report_generator


@app.route('/')
def index():
    """Main dashboard page."""
    today = date.today()
    
    # Get today's transactions
    today_transactions = tm.get_transactions_by_date(today)
    
    # Get today's summary
    today_summary = tm.get_transaction_summary(today, today)
    
    # Get this week's summary
    week_start, week_end = DateUtils.get_week_range(today)
    week_summary = tm.get_transaction_summary(week_start, week_end)
    
    # Get this month's summary
    month_start, month_end = DateUtils.get_month_range(today)
    month_summary = tm.get_transaction_summary(month_start, month_end)
    
    # Get recent transactions (last 10)
    recent_transactions = tm.get_transactions(limit=10, order_by="created_at DESC")
    
    # Get top categories this month
    top_categories = tm.get_category_summary(month_start, month_end)[:5]
    
    return render_template('dashboard.html',
                         today_transactions=today_transactions,
                         today_summary=today_summary,
                         week_summary=week_summary,
                         month_summary=month_summary,
                         recent_transactions=recent_transactions,
                         top_categories=top_categories,
                         today=today)


@app.route('/add_transaction')
def add_transaction_page():
    """Add transaction page."""
    categories = tm.get_categories()
    expense_categories = [c for c in categories if c['type'] == 'expense']
    income_categories = [c for c in categories if c['type'] == 'income']
    
    return render_template('add_transaction.html',
                         expense_categories=expense_categories,
                         income_categories=income_categories)


@app.route('/api/add_transaction', methods=['POST'])
def api_add_transaction():
    """API endpoint to add a new transaction."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['type', 'amount', 'date']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Validate amount
        is_valid_amount, amount, amount_error = Validators.validate_amount(str(data['amount']))
        if not is_valid_amount:
            return jsonify({'success': False, 'message': amount_error}), 400
        
        # Validate date
        is_valid_date, transaction_date, date_error = Validators.validate_date_input(data['date'])
        if not is_valid_date:
            return jsonify({'success': False, 'message': date_error}), 400
        
        # Add transaction
        success, transaction_id, message = tm.add_transaction(
            transaction_type=data['type'],
            amount=amount,
            category_id=data.get('category_id') if data.get('category_id') else None,
            description=data.get('description'),
            transaction_date=transaction_date
        )
        
        if success:
            # Get the added transaction for response
            transaction = tm.get_transaction_by_id(transaction_id)
            return jsonify({
                'success': True,
                'message': message,
                'transaction': {
                    'id': transaction.id,
                    'type': transaction.type,
                    'amount': transaction.amount,
                    'description': transaction.description,
                    'date': transaction.transaction_date.isoformat(),
                    'category_name': transaction.category_name
                }
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/transactions')
def transactions_page():
    """Transactions listing page."""
    # Get filter parameters
    date_filter = request.args.get('date', '')
    type_filter = request.args.get('type', '')
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '')
    
    # Parse date filter
    start_date = None
    end_date = None
    
    if date_filter:
        if date_filter in ['today', 'yesterday', 'this_week', 'this_month', 'this_year']:
            if date_filter == 'today':
                start_date = end_date = date.today()
            elif date_filter == 'yesterday':
                start_date = end_date = date.today() - timedelta(days=1)
            elif date_filter == 'this_week':
                start_date, end_date = DateUtils.get_week_range()
            elif date_filter == 'this_month':
                start_date, end_date = DateUtils.get_month_range()
            elif date_filter == 'this_year':
                start_date, end_date = DateUtils.get_year_range()
        else:
            # Try parsing custom date range
            date_range = DateUtils.parse_date_range(date_filter)
            if date_range:
                start_date, end_date = date_range
    
    # Get transactions
    if search_query:
        transactions = tm.search_transactions(search_query, 100)
    else:
        transactions = tm.get_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type=type_filter if type_filter else None,
            category_id=int(category_filter) if category_filter else None,
            limit=100
        )
    
    # Get summary for the filtered results
    summary = tm.get_transaction_summary(start_date, end_date) if start_date and end_date else None
    
    # Get categories for filter dropdown
    categories = tm.get_categories()
    
    return render_template('transactions.html',
                         transactions=transactions,
                         summary=summary,
                         categories=categories,
                         filters={
                             'date': date_filter,
                             'type': type_filter,
                             'category': category_filter,
                             'search': search_query
                         })


@app.route('/api/delete_transaction/<int:transaction_id>', methods=['DELETE'])
def api_delete_transaction(transaction_id):
    """API endpoint to delete a transaction."""
    try:
        success, message = tm.delete_transaction(transaction_id)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/update_transaction/<int:transaction_id>', methods=['PUT'])
def api_update_transaction(transaction_id):
    """API endpoint to update a transaction."""
    try:
        data = request.get_json()
        
        update_params = {}
        
        if 'type' in data:
            update_params['transaction_type'] = data['type']
        
        if 'amount' in data:
            is_valid_amount, amount, amount_error = Validators.validate_amount(str(data['amount']))
            if not is_valid_amount:
                return jsonify({'success': False, 'message': amount_error}), 400
            update_params['amount'] = amount
        
        if 'category_id' in data:
            update_params['category_id'] = data['category_id'] if data['category_id'] else None
        
        if 'description' in data:
            update_params['description'] = data['description']
        
        if 'date' in data:
            is_valid_date, transaction_date, date_error = Validators.validate_date_input(data['date'])
            if not is_valid_date:
                return jsonify({'success': False, 'message': date_error}), 400
            update_params['transaction_date'] = transaction_date
        
        success, message = tm.update_transaction(transaction_id, **update_params)
        
        if success:
            # Get updated transaction
            transaction = tm.get_transaction_by_id(transaction_id)
            return jsonify({
                'success': True,
                'message': message,
                'transaction': {
                    'id': transaction.id,
                    'type': transaction.type,
                    'amount': transaction.amount,
                    'description': transaction.description,
                    'date': transaction.transaction_date.isoformat(),
                    'category_name': transaction.category_name
                }
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/reports')
def reports_page():
    """Reports page."""
    report_type = request.args.get('type', 'monthly')
    target_date = request.args.get('date', '')
    
    # Parse target date
    if target_date:
        parsed_date = DateUtils.parse_date(target_date)
    else:
        parsed_date = date.today()
    
    # Generate report based on type
    if report_type == 'daily':
        report_data = rg.generate_daily_report(parsed_date)
    elif report_type == 'weekly':
        report_data = rg.generate_weekly_report(parsed_date)
    elif report_type == 'monthly':
        report_data = rg.generate_monthly_report(parsed_date)
    elif report_type == 'yearly':
        report_data = rg.generate_yearly_report(parsed_date)
    else:
        report_data = rg.generate_monthly_report(parsed_date)
        report_type = 'monthly'
    
    return render_template('reports.html',
                         report_data=report_data,
                         report_type=report_type,
                         target_date=parsed_date)


@app.route('/categories')
def categories_page():
    """Categories management page."""
    categories = tm.get_categories()
    expense_categories = [c for c in categories if c['type'] == 'expense']
    income_categories = [c for c in categories if c['type'] == 'income']
    
    return render_template('categories.html',
                         expense_categories=expense_categories,
                         income_categories=income_categories)


@app.route('/api/add_category', methods=['POST'])
def api_add_category():
    """API endpoint to add a new category."""
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['name', 'type']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        success, category_id, message = tm.add_category(data['name'], data['type'])
        
        if success:
            category = tm.get_category_by_id(category_id)
            return jsonify({
                'success': True,
                'message': message,
                'category': category
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/delete_category/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id):
    """API endpoint to delete a category."""
    try:
        success, message = tm.delete_category(category_id)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/dashboard_data')
def api_dashboard_data():
    """API endpoint to get dashboard data."""
    try:
        today = date.today()
        
        # Get summaries for different periods
        today_summary = tm.get_transaction_summary(today, today)
        
        week_start, week_end = DateUtils.get_week_range(today)
        week_summary = tm.get_transaction_summary(week_start, week_end)
        
        month_start, month_end = DateUtils.get_month_range(today)
        month_summary = tm.get_transaction_summary(month_start, month_end)
        
        # Get recent transactions
        recent_transactions = tm.get_transactions(limit=5, order_by="created_at DESC")
        
        return jsonify({
            'success': True,
            'data': {
                'today': {
                    'income': today_summary.total_income,
                    'expenses': today_summary.total_expenses,
                    'net': today_summary.net_balance,
                    'count': today_summary.transaction_count
                },
                'week': {
                    'income': week_summary.total_income,
                    'expenses': week_summary.total_expenses,
                    'net': week_summary.net_balance,
                    'count': week_summary.transaction_count
                },
                'month': {
                    'income': month_summary.total_income,
                    'expenses': month_summary.total_expenses,
                    'net': month_summary.net_balance,
                    'count': month_summary.transaction_count
                },
                'recent_transactions': [
                    {
                        'id': t.id,
                        'type': t.type,
                        'amount': t.amount,
                        'description': t.description,
                        'date': t.transaction_date.isoformat(),
                        'category_name': t.category_name
                    } for t in recent_transactions
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    """Format amount as currency."""
    return f"${amount:.2f}"


@app.template_filter('date_format')
def date_format_filter(date_obj, format_type='default'):
    """Format date for display."""
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj).date()
    return DateUtils.format_date(date_obj, format_type)


@app.template_filter('relative_date')
def relative_date_filter(date_obj):
    """Get relative date string."""
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj).date()
    return DateUtils.get_relative_date_string(date_obj)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

