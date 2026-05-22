"""
PS_RevenueTracker Main Entry Point
Launches the LDAP login screen
"""

import sys
import os

# Add auth directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'auth'))

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from auth.login_screen import LoginScreen
from config.ldap_config import get_ldap_config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window after successful login"""
    
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.init_ui()
    
    def init_ui(self):
        """Initialize main window UI"""
        self.setWindowTitle("PS_RevenueTracker - Dashboard")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Welcome label
        welcome_label = QLabel(f"Welcome, {self.username}!")
        welcome_font = QFont()
        welcome_font.setPointSize(16)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Placeholder for main content
        content_label = QLabel("Revenue Tracker Dashboard\n\n(Main application content goes here)")
        content_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(content_label)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def closeEvent(self, event):
        """Handle window close event"""
        logger.info(f"User '{self.username}' logged out")
        event.accept()


def on_login_success(username: str):
    """Callback when user successfully logs in"""
    logger.info(f"User '{username}' authenticated successfully")
    
    # Hide login screen and show main window
    login_window.hide()
    main_window = MainWindow(username)
    main_window.show()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logger.info("PS_RevenueTracker application starting")
    
    # Get LDAP configuration
    ldap_config = get_ldap_config()
    
    # Create and show login screen
    global login_window
    login_window = LoginScreen(ldap_config, on_login_success)
    login_window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()