"""
Login Screen UI with LDAP Integration
Provides a PyQt5-based login interface for PS_RevenueTracker
"""

import sys
import logging
from typing import Optional, Callable
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont, QPixmap
from ldap_auth import LDAPAuthenticator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AuthenticationWorker(QThread):
    """Background worker thread for LDAP authentication"""
    
    auth_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, authenticator: LDAPAuthenticator, username: str, password: str):
        super().__init__()
        self.authenticator = authenticator
        self.username = username
        self.password = password
    
    def run(self):
        """Run authentication in background thread"""
        try:
            success, user_dn = self.authenticator.authenticate_user(self.username, self.password)
            if success:
                self.auth_complete.emit(True, f"Welcome, {self.username}!")
            else:
                self.auth_complete.emit(False, "Invalid username or password")
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.auth_complete.emit(False, f"Authentication error: {str(e)}")


class LoginScreen(QWidget):
    """Main login screen widget"""
    
    login_successful = pyqtSignal(str)  # Emit username on successful login
    
    def __init__(self, ldap_config: dict, on_login_success: Optional[Callable] = None):
        """
        Initialize login screen
        
        Args:
            ldap_config: Dictionary containing LDAP configuration
                - ldap_server: LDAP server address
                - ldap_port: LDAP port (default: 389)
                - base_dn: Base Distinguished Name
                - use_tls: Use TLS/SSL (default: False)
            on_login_success: Callback function on successful login
        """
        super().__init__()
        self.ldap_config = ldap_config
        self.on_login_success = on_login_success
        self.auth_worker = None
        
        # Initialize LDAP authenticator
        self.authenticator = LDAPAuthenticator(
            ldap_server=ldap_config.get('ldap_server', 'localhost'),
            ldap_port=ldap_config.get('ldap_port', 389),
            base_dn=ldap_config.get('base_dn', 'dc=example,dc=com'),
            use_tls=ldap_config.get('use_tls', False)
        )
        
        # Verify LDAP connection
        if not self.authenticator.verify_connection():
            logger.warning("Could not verify LDAP connection at startup")
        
        self.init_ui()
        self.login_successful.connect(self._on_login_success)
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("PS_RevenueTracker - Login")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet(self._get_stylesheet())
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("PS_RevenueTracker")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("LDAP Authentication")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666;")
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(10)
        
        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username or email")
        self.username_input.setMinimumHeight(35)
        self.username_input.returnPressed.connect(self.attempt_login)
        main_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self.attempt_login)
        main_layout.addWidget(self.password_input)
        
        # Remember me
        self.remember_me = QCheckBox("Remember me")
        main_layout.addWidget(self.remember_me)
        
        main_layout.addSpacing(10)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003d82;
            }
        """)
        self.login_button.clicked.connect(self.attempt_login)
        button_layout.addWidget(self.login_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #CCCCCC;
                color: black;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #BBBBBB;
            }
        """)
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #FF0000; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
    
    def attempt_login(self):
        """Attempt to authenticate user"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Disable login button and show loading state
        self.login_button.setEnabled(False)
        self.login_button.setText("Authenticating...")
        self.status_label.setText("Authenticating...")
        self.status_label.setStyleSheet("color: #0066CC; font-style: italic;")
        
        # Create and start authentication worker
        self.auth_worker = AuthenticationWorker(self.authenticator, username, password)
        self.auth_worker.auth_complete.connect(self._handle_auth_result)
        self.auth_worker.start()
    
    def _handle_auth_result(self, success: bool, message: str):
        """Handle authentication result"""
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")
        
        if success:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #00AA00; font-style: italic;")
            username = self.username_input.text().strip()
            self.login_successful.emit(username)
        else:
            self.show_error(message)
    
    def show_error(self, message: str):
        """Show error message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #FF0000; font-style: italic;")
        logger.warning(f"Login error: {message}")
    
    def clear_fields(self):
        """Clear all input fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.status_label.setText("")
        self.username_input.setFocus()
    
    def _on_login_success(self, username: str):
        """Handle successful login"""
        logger.info(f"User '{username}' logged in successfully")
        if self.on_login_success:
            self.on_login_success(username)
        else:
            QMessageBox.information(self, "Success", f"Welcome, {username}!\n\nYou have been successfully authenticated.")
    
    def _get_stylesheet(self) -> str:
        """Get application stylesheet"""
        return """
            QWidget {
                background-color: #F5F5F5;
                font-family: 'Arial', sans-serif;
                font-size: 11px;
            }
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                selection-background-color: #007AFF;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
            }
            QLabel {
                color: #333333;
            }
            QCheckBox {
                color: #333333;
            }
        """


def main():
    """Run login screen application"""
    app = QApplication(sys.argv)
    
    # LDAP Configuration
    ldap_config = {
        'ldap_server': 'localhost',  # Change to your LDAP server
        'ldap_port': 389,
        'base_dn': 'dc=example,dc=com',  # Change to your base DN
        'use_tls': False
    }
    
    def on_login_success(username):
        """Callback on successful login"""
        print(f"User {username} logged in successfully!")
        # Here you would typically open the main application window
        sys.exit(0)
    
    login_screen = LoginScreen(ldap_config, on_login_success)
    login_screen.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()