"""
Main entry point for the Clinical Data Extractor application.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Load app configuration
    try:
        from src.utils.config_manager import ConfigManager
        config_manager = ConfigManager()
        app_config = config_manager.load_app_config()
        
        # Set application properties from config
        app.setApplicationName(app_config['app_title'])
        app.setApplicationVersion(app_config['version'])
        app.setOrganizationName(app_config.get('organization', 'Metanome'))
    except Exception:
        # Fallback values if config loading fails
        app.setApplicationName("Clinical Data Extractor")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Metanome")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply dark theme (optional)
    # app.setStyleSheet(get_dark_theme())
    
    try:
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        QMessageBox.critical(
            None, "Application Error",
            f"Failed to start the application:\n\n{str(e)}"
        )
        sys.exit(1)


def get_dark_theme():
    """Get dark theme stylesheet (optional)."""
    return """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QGroupBox {
        color: #ffffff;
        border: 2px solid #555555;
    }
    QLineEdit {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        color: #ffffff;
        padding: 5px;
    }
    QTextEdit {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        color: #ffffff;
    }
    QProgressBar {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #0078d4;
    }
    """


if __name__ == "__main__":
    main()
