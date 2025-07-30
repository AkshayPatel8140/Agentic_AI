#!/usr/bin/env python3
"""
Startup script for the Daily Expense & Income Tracker Web Application.
"""

import os
import sys
import webbrowser
from threading import Timer

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from web_app import app
except ImportError as e:
    print("❌ Error importing web application:")
    print(f"   {e}")
    print("\n💡 Make sure you have installed the required dependencies:")
    print("   pip install Flask>=2.3.0")
    sys.exit(1)


def open_browser():
    """Open the web browser to the application URL."""
    webbrowser.open('http://localhost:5000')


def main():
    """Main function to start the web application."""
    print("💰 Daily Expense & Income Tracker - Web Application")
    print("=" * 55)
    print()
    
    # Check if Flask is available
    try:
        import flask
        print(f"✅ Flask version: {flask.__version__}")
    except ImportError:
        print("❌ Flask is not installed!")
        print("💡 Install it with: pip install Flask>=2.3.0")
        sys.exit(1)
    
    # Set up the database
    print("🗄️  Initializing database...")
    try:
        from database import db
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Configuration
    host = os.getenv('EXPENSE_TRACKER_HOST', '127.0.0.1')
    port = int(os.getenv('EXPENSE_TRACKER_PORT', 5000))
    debug = os.getenv('EXPENSE_TRACKER_DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Starting web server on http://{host}:{port}")
    print("📊 Features available:")
    print("   • Dashboard with real-time summaries")
    print("   • Add/edit transactions with date selection")
    print("   • Comprehensive reporting and charts")
    print("   • Category management")
    print("   • Transaction search and filtering")
    print()
    
    if debug:
        print("🔧 Running in DEBUG mode")
        print("⚠️  For production, set EXPENSE_TRACKER_DEBUG=False")
        print()
    
    print("🚀 Starting application...")
    print("📝 Access the web interface at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Open browser after a short delay
    if not os.getenv('EXPENSE_TRACKER_NO_BROWSER'):
        Timer(1.5, open_browser).start()
    
    try:
        # Start the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

