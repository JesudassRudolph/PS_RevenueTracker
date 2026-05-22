"""
PS_RevenueTracker Web Application
Flask-based LDAP authentication system
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from datetime import datetime, timedelta
import logging
import os
import sys
from functools import wraps

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.ldap_auth import LDAPAuthenticator
from config.ldap_config import get_ldap_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your-secret-key-change-this-in-production'

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
Session(app)

# Get LDAP configuration
ldap_config = get_ldap_config()
ldap_auth = LDAPAuthenticator(
    ldap_server=ldap_config.get('ldap_server', 'localhost'),
    ldap_port=ldap_config.get('ldap_port', 389),
    base_dn=ldap_config.get('base_dn', 'dc=example,dc=com'),
    use_tls=ldap_config.get('use_tls', False)
)


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET'])
def login():
    """Login page"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        # Validate input
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Authenticate user
        success, user_dn = ldap_auth.authenticate_user(username, password)
        
        if success:
            # Store user in session
            session['user'] = username
            session['user_dn'] = user_dn
            session['login_time'] = datetime.now().isoformat()
            session.permanent = remember_me
            
            logger.info(f"User '{username}' logged in successfully")
            
            return jsonify({
                'success': True,
                'message': f'Welcome, {username}!',
                'redirect': url_for('dashboard')
            }), 200
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Authentication error: {str(e)}'
        }), 500


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    user = session.get('user')
    login_time = session.get('login_time')
    return render_template('dashboard.html', user=user, login_time=login_time)


@app.route('/api/user-info')
@login_required
def api_user_info():
    """Get current user information"""
    user = session.get('user')
    login_time = session.get('login_time')
    
    return jsonify({
        'username': user,
        'login_time': login_time,
        'session_timeout': app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
    }), 200


@app.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    user = session.get('user')
    session.clear()
    
    if user:
        logger.info(f"User '{user}' logged out")
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully',
        'redirect': url_for('login')
    }), 200


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        ldap_connected = ldap_auth.verify_connection()
        return jsonify({
            'status': 'healthy',
            'ldap_connected': ldap_connected
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('flask_sessions', exist_ok=True)
    
    logger.info("Starting PS_RevenueTracker Web Application")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)