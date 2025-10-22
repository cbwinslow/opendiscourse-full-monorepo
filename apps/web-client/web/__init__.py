"""
Initialization script for OpenDiscourse web application.

This script sets up the Flask application and runs it.
"""

import os
import sys
from opendiscourse.web.app import create_app

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    """Main entry point for the web application."""
    # Determine configuration
    config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Create the Flask application
    app = create_app(config_name)
    
    # Run the application
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )

if __name__ == '__main__':
    main()