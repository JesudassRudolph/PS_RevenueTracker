"""
LDAP Configuration Settings
Update these values to match your local LDAP setup
"""

# LDAP Server Configuration
LDAP_SERVER = 'localhost'  # LDAP server address
LDAP_PORT = 389            # Standard LDAP port (636 for LDAPS)
USE_TLS = False            # Set to True for LDAPS or STARTTLS

# LDAP Directory Configuration
BASE_DN = 'dc=example,dc=com'  # Base Distinguished Name
SEARCH_OU = 'ou=users'         # Organizational Unit for users

# Admin Credentials (for admin queries only)
ADMIN_DN = 'cn=admin,dc=example,dc=com'
ADMIN_PASSWORD = 'admin_password_here'

# LDAP Search Attributes
SEARCH_ATTRIBUTES = ['uid', 'mail', 'cn', 'displayName', 'department']

# Application Configuration
APP_NAME = "PS_RevenueTracker"
REMEMBER_ME_DURATION = 30  # Days to remember login
SESSION_TIMEOUT = 1800     # Session timeout in seconds (30 minutes)

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/auth.log'

# Security Settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # Seconds (15 minutes)
PASSWORD_MIN_LENGTH = 8


def get_ldap_config():
    """Get LDAP configuration as dictionary"""
    return {
        'ldap_server': LDAP_SERVER,
        'ldap_port': LDAP_PORT,
        'base_dn': BASE_DN,
        'use_tls': USE_TLS,
        'admin_dn': ADMIN_DN,
        'admin_password': ADMIN_PASSWORD
    }