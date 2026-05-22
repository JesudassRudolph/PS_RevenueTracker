"""
LDAP Authentication Module for PS_RevenueTracker
Handles user authentication against local LDAP directory
"""

import ldap
import ldap.modlist as modlist
from ldap.filter import escape_filter_chars
import logging
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)


class LDAPAuthenticator:
    """Handles LDAP authentication and user management"""
    
    def __init__(self, ldap_server: str, ldap_port: int = 389, 
                 base_dn: str = "dc=example,dc=com", use_tls: bool = False):
        """
        Initialize LDAP Authenticator
        
        Args:
            ldap_server: LDAP server address (e.g., 'ldap.example.com' or 'localhost')
            ldap_port: LDAP server port (default: 389, 636 for LDAPS)
            base_dn: Base Distinguished Name for LDAP directory
            use_tls: Whether to use TLS/SSL encryption
        """
        self.ldap_server = ldap_server
        self.ldap_port = ldap_port
        self.base_dn = base_dn
        self.use_tls = use_tls
        self.ldap_uri = f"ldap://{ldap_server}:{ldap_port}"
        if use_tls:
            self.ldap_uri = f"ldaps://{ldap_server}:{ldap_port}"
        
        logger.info(f"LDAP Authenticator initialized with URI: {self.ldap_uri}")
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate user against LDAP directory
        
        Args:
            username: Username (can be username or email)
            password: User's password
            
        Returns:
            Tuple of (success: bool, user_dn: str or None)
        """
        if not username or not password:
            logger.warning("Authentication attempted with empty credentials")
            return False, None
        
        try:
            # Connect to LDAP server
            conn = ldap.initialize(self.ldap_uri)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 10)
            
            # Search for user
            search_filter = f"(|(uid={escape_filter_chars(username)})(mail={escape_filter_chars(username)}))"
            logger.debug(f"Searching LDAP with filter: {search_filter}")
            
            result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, search_filter, ['uid', 'mail', 'cn'])
            
            if not result:
                logger.warning(f"User not found in LDAP: {username}")
                conn.unbind_s()
                return False, None
            
            user_dn = result[0][0]
            user_attrs = result[0][1]
            
            # Attempt to bind with user's credentials
            user_conn = ldap.initialize(self.ldap_uri)
            user_conn.set_option(ldap.OPT_REFERRALS, 0)
            user_conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 10)
            
            try:
                user_conn.simple_bind_s(user_dn, password)
                logger.info(f"Successful authentication for user: {username}")
                user_conn.unbind_s()
                conn.unbind_s()
                return True, user_dn
            except ldap.INVALID_CREDENTIALS:
                logger.warning(f"Invalid credentials for user: {username}")
                conn.unbind_s()
                return False, None
                
        except ldap.SERVER_DOWN:
            logger.error("LDAP server is unavailable")
            return False, None
        except ldap.TIMEOUT:
            logger.error("LDAP connection timeout")
            return False, None
        except Exception as e:
            logger.error(f"LDAP authentication error: {str(e)}")
            return False, None
    
    def get_user_info(self, username: str, admin_dn: str, admin_password: str) -> Optional[Dict]:
        """
        Retrieve user information from LDAP (requires admin credentials)
        
        Args:
            username: Username to retrieve info for
            admin_dn: Admin user's Distinguished Name
            admin_password: Admin user's password
            
        Returns:
            Dictionary of user attributes or None if not found
        """
        try:
            conn = ldap.initialize(self.ldap_uri)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 10)
            
            # Bind as admin
            conn.simple_bind_s(admin_dn, admin_password)
            
            # Search for user
            search_filter = f"(|(uid={escape_filter_chars(username)})(mail={escape_filter_chars(username)}))"
            result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, search_filter)
            
            if result:
                user_dn = result[0][0]
                user_attrs = result[0][1]
                
                # Convert byte strings to strings
                user_info = {
                    'dn': user_dn,
                    'uid': user_attrs.get('uid', [b''])[0].decode('utf-8'),
                    'cn': user_attrs.get('cn', [b''])[0].decode('utf-8'),
                    'mail': user_attrs.get('mail', [b''])[0].decode('utf-8'),
                }
                
                conn.unbind_s()
                return user_info
            
            conn.unbind_s()
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving user info: {str(e)}")
            return None
    
    def verify_connection(self) -> bool:
        """
        Verify LDAP server connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            conn = ldap.initialize(self.ldap_uri)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 5)
            conn.simple_bind_s()
            conn.unbind_s()
            logger.info("LDAP server connection verified")
            return True
        except Exception as e:
            logger.error(f"LDAP connection verification failed: {str(e)}")
            return False
