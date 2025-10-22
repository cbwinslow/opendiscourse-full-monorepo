'''
Main Flask Application for OpenDiscourse

This module defines the main Flask application and its configuration.
'''

import os
import logging
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration name ('default', 'development', 'testing', 'production')
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('opendiscourse.web.config')
    
    # Override with environment variables if available
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/opendiscourse'
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from opendiscourse.web.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from opendiscourse.web.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('500.html'), 500
    
    # Register template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d'):
        """Format datetime objects in templates."""
        if value is None:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        return value.strftime(format)
    
    @app.template_filter('truncate')
    def truncate_text(text, length=100):
        """Truncate text to specified length."""
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    logger.info("Flask application created")
    return app

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)