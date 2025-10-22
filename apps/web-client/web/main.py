"""
Main Blueprint for OpenDiscourse Web Application

This module defines the main routes for the web application.
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main index page."""
    return render_template('index.html', title='OpenDiscourse - Government Transparency')

@bp.route('/about')
def about():
    """About page."""
    return render_template('about.html', title='About OpenDiscourse')

@bp.route('/search')
def search():
    """Search page."""
    query = request.args.get('q', '')
    return render_template('search.html', title='Search', query=query)

@bp.route('/members')
def members():
    """Members directory page."""
    return render_template('members.html', title='Government Members')

@bp.route('/bills')
def bills():
    """Bills page."""
    return render_template('bills.html', title='Legislation')

@bp.route('/member/<person_id>')
def member_profile(person_id):
    """Member profile page."""
    return render_template('member_profile.html', title='Member Profile', person_id=person_id)

@bp.route('/bill/<bill_id>')
def bill_details(bill_id):
    """Bill details page."""
    return render_template('bill_details.html', title='Bill Details', bill_id=bill_id)

@bp.route('/discrepancies')
def discrepancies():
    """Discrepancies page."""
    return render_template('discrepancies.html', title='Identified Discrepancies')

@bp.route('/api/docs')
def api_docs():
    """API documentation page."""
    return render_template('api_docs.html', title='API Documentation')

@bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html', title='Contact Us')

@bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('privacy.html', title='Privacy Policy')

@bp.route('/terms')
def terms():
    """Terms of service page."""
    return render_template('terms.html', title='Terms of Service')

# Error handlers
@bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html', title='Page Not Found'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    current_app.logger.error(f'Server Error: {error}')
    return render_template('500.html', title='Server Error'), 500

# Health check endpoint
@bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })