"""
Main application window for the Clinical Data Extractor.
"""

import os
import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QGroupBox, QFrame, QApplication,
    QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction

from ..utils.config_manager import ConfigManager
from ..core.extraction_engine import ExtractionEngine


class ExtractionWorker(QThread):
    """Worker thread for data extraction to keep UI responsive."""
    
    progress_updated = pyqtSignal(int, str)
    extraction_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, engine: ExtractionEngine, root_folder: str, 
                 subject_list_file: str, target_filename: str):
        super().__init__()
        self.engine = engine
        self.root_folder = root_folder
        self.subject_list_file = subject_list_file
        self.target_filename = target_filename
    
    def run(self):
        """Run the extraction process in a separate thread."""
        try:
            results = self.engine.extract_data(
                self.root_folder,
                self.subject_list_file,
                self.target_filename,
                self.progress_callback
            )
            self.extraction_completed.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def progress_callback(self, percentage: int, message: str):
        """Callback for progress updates."""
        self.progress_updated.emit(percentage, message)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.app_config = self.config_manager.load_app_config()
        self.extraction_rules = self.config_manager.load_extraction_rules()
        
        self.extraction_worker = None
        self.extraction_results = None
        self.tesseract_available = False
        
        self.init_ui()
        self.init_menu()
        self.init_status_bar()
        
        # Check system dependencies after UI is loaded
        QTimer.singleShot(500, self.check_system_dependencies)
        
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle(f"{self.app_config['app_title']} v{self.app_config['version']}")
        self.setGeometry(100, 100, *self.app_config['window_size'])
        self.setMinimumSize(*self.app_config.get('minimum_window_size', [800, 600]))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add header
        self.create_header(main_layout)
        
        # Add file selection section
        self.create_file_selection_section(main_layout)
        
        # Add target configuration section
        self.create_target_config_section(main_layout)
        
        # Add controls section
        self.create_controls_section(main_layout)
        
        # Add progress section
        self.create_progress_section(main_layout)
        
        # Add log section
        self.create_log_section(main_layout)
    
    def create_header(self, layout: QVBoxLayout):
        """Create application header."""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel(self.app_config['app_title'])
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Automated Clinical Data Extraction Tool")
        subtitle_label.setStyleSheet("""
            color: #ecf0f1;
            font-size: 14px;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def create_file_selection_section(self, layout: QVBoxLayout):
        """Create file/folder selection section."""
        group_box = QGroupBox("File Selection")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout_grid = QGridLayout(group_box)
        layout_grid.setSpacing(10)
        
        # Data folder selection
        layout_grid.addWidget(QLabel("Data Folder:"), 0, 0)
        self.data_folder_edit = QLineEdit()
        self.data_folder_edit.setPlaceholderText("Select the root network folder...")
        layout_grid.addWidget(self.data_folder_edit, 0, 1)
        
        self.browse_folder_btn = QPushButton("Browse")
        self.browse_folder_btn.clicked.connect(self.browse_data_folder)
        self.browse_folder_btn.setStyleSheet(self._get_button_style("#3498db"))
        layout_grid.addWidget(self.browse_folder_btn, 0, 2)
        
        # Subject list file selection
        layout_grid.addWidget(QLabel("Subject List:"), 1, 0)
        self.subject_list_edit = QLineEdit()
        self.subject_list_edit.setPlaceholderText("Select subject list .txt file...")
        layout_grid.addWidget(self.subject_list_edit, 1, 1)
        
        self.browse_subjects_btn = QPushButton("Browse")
        self.browse_subjects_btn.clicked.connect(self.browse_subject_list)
        self.browse_subjects_btn.setStyleSheet(self._get_button_style("#3498db"))
        layout_grid.addWidget(self.browse_subjects_btn, 1, 2)
        
        layout.addWidget(group_box)
    
    def create_target_config_section(self, layout: QVBoxLayout):
        """Create target configuration section."""
        group_box = QGroupBox("Target Configuration")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout_grid = QGridLayout(group_box)
        layout_grid.setSpacing(10)
        
        layout_grid.addWidget(QLabel("Target Filename:"), 0, 0)
        self.target_filename_edit = QLineEdit()
        self.target_filename_edit.setPlaceholderText("e.g., A_RAPOR_1.jpg, summary.pdf")
        self.target_filename_edit.setText("A_RAPOR_1.jpg")  # Default value
        layout_grid.addWidget(self.target_filename_edit, 0, 1)
        
        layout.addWidget(group_box)
    
    def create_controls_section(self, layout: QVBoxLayout):
        """Create controls section."""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        # Start extraction button
        self.start_btn = QPushButton("Start Extraction")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet(self._get_button_style("#27ae60", 16))
        self.start_btn.clicked.connect(self.start_extraction)
        controls_layout.addWidget(self.start_btn)
        
        # Settings button
        self.settings_btn = QPushButton("Manage Rules")
        self.settings_btn.setMinimumHeight(50)
        self.settings_btn.setStyleSheet(self._get_button_style("#f39c12", 16))
        self.settings_btn.clicked.connect(self.open_settings)
        controls_layout.addWidget(self.settings_btn)
        
        # Export button
        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.setMinimumHeight(50)
        self.export_btn.setStyleSheet(self._get_button_style("#9b59b6", 16))
        self.export_btn.clicked.connect(self.export_to_excel)
        self.export_btn.setEnabled(False)
        controls_layout.addWidget(self.export_btn)
        
        layout.addLayout(controls_layout)
    
    def create_progress_section(self, layout: QVBoxLayout):
        """Create progress tracking section."""
        group_box = QGroupBox("Progress")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        progress_layout = QVBoxLayout(group_box)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to start extraction")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(group_box)
    
    def create_log_section(self, layout: QVBoxLayout):
        """Create log display section."""
        group_box = QGroupBox("Activity Log")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        log_layout = QVBoxLayout(group_box)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                font-family: Consolas, monospace;
                font-size: 10px;
                padding: 5px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(group_box)
    
    def init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Session', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_session)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_status_bar(self):
        """Initialize status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _get_button_style(self, color: str, font_size: int = 12) -> str:
        """Get consistent button styling."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
        """
    
    def browse_data_folder(self):
        """Browse for data folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Data Folder", "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        if folder:
            self.data_folder_edit.setText(folder)
            self.log_message(f"Data folder selected: {folder}")
    
    def browse_subject_list(self):
        """Browse for subject list file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Subject List File", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.subject_list_edit.setText(file_path)
            self.log_message(f"Subject list file selected: {file_path}")
    
    def start_extraction(self):
        """Start the data extraction process."""
        # Validate inputs
        if not self.validate_inputs():
            return
        
        # Disable controls
        self.set_controls_enabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_label.setText("Initializing extraction...")
        
        # Create extraction engine
        engine = ExtractionEngine(self.app_config, self.extraction_rules)
        
        # Create and start worker thread
        self.extraction_worker = ExtractionWorker(
            engine,
            self.data_folder_edit.text(),
            self.subject_list_edit.text(),
            self.target_filename_edit.text()
        )
        
        self.extraction_worker.progress_updated.connect(self.update_progress)
        self.extraction_worker.extraction_completed.connect(self.extraction_completed)
        self.extraction_worker.error_occurred.connect(self.extraction_error)
        
        self.extraction_worker.start()
        
        self.log_message("Extraction started...")
    
    def set_controls_enabled(self, enabled: bool):
        """Enable/disable controls during extraction."""
        self.start_btn.setEnabled(enabled)
        self.browse_folder_btn.setEnabled(enabled)
        self.browse_subjects_btn.setEnabled(enabled)
        self.data_folder_edit.setEnabled(enabled)
        self.subject_list_edit.setEnabled(enabled)
        self.target_filename_edit.setEnabled(enabled)
    
    def update_progress(self, percentage: int, message: str):
        """Update progress bar and label."""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)
        self.log_message(f"Progress: {percentage}% - {message}")
    
    def extraction_completed(self, results: Dict[str, Any]):
        """Handle extraction completion."""
        self.extraction_results = results
        self.set_controls_enabled(True)
        
        if results['success']:
            self.export_btn.setEnabled(True)
            self.log_message(f"Extraction completed successfully!")
            self.log_message(f"Processed: {results['processed_subjects']} subjects")
            self.log_message(f"Successful extractions: {results['successful_extractions']}")
            self.log_message(f"Failed extractions: {results['failed_extractions']}")
            
            # Log warnings if any
            if 'warnings' in results:
                for warning in results['warnings']:
                    self.log_message(f"WARNING: {warning}")
            
            # Prepare completion message
            completion_msg = (
                f"Extraction completed successfully!\n\n"
                f"Processed: {results['processed_subjects']} subjects\n"
                f"Successful: {results['successful_extractions']}\n"
                f"Failed: {results['failed_extractions']}"
            )
            
            # Add missing subjects warning if any
            if 'missing_subjects' in results:
                missing_count = len(results['missing_subjects'])
                missing_list = ', '.join(results['missing_subjects'])
                completion_msg += f"\n\nWarning: {missing_count} subjects not found in data folder:\n{missing_list}"
            
            QMessageBox.information(
                self, "Extraction Complete", completion_msg
            )
        else:
            self.log_message("Extraction failed:")
            for error in results.get('errors', []):
                self.log_message(f"  - {error}")
            
            QMessageBox.critical(
                self, "Extraction Failed",
                f"Extraction failed:\n\n" + "\n".join(results.get('errors', []))
            )
        
        self.status_bar.showMessage("Extraction completed")
    
    def extraction_error(self, error_message: str):
        """Handle extraction error."""
        self.set_controls_enabled(True)
        self.log_message(f"Extraction error: {error_message}")
        QMessageBox.critical(self, "Extraction Error", f"An error occurred during extraction:\n\n{error_message}")
        self.status_bar.showMessage("Extraction failed")
    
    def export_to_excel(self):
        """Export results to Excel."""
        if not self.extraction_results:
            QMessageBox.warning(self, "Export Error", "No extraction results available.")
            return
        
        # Get output file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel Report", "extraction_results.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            # Create extraction engine for export
            engine = ExtractionEngine(self.app_config, self.extraction_rules)
            
            success = engine.generate_excel_report(self.extraction_results, file_path)
            
            if success:
                self.log_message(f"Excel report exported to: {file_path}")
                QMessageBox.information(
                    self, "Export Successful",
                    f"Excel report has been exported successfully to:\n\n{file_path}"
                )
            else:
                self.log_message("Failed to export Excel report")
                QMessageBox.critical(
                    self, "Export Failed",
                    "Failed to export Excel report. Please check the log for details."
                )
    
    def open_settings(self):
        """Open settings/rules management window."""
        from .settings_window import SettingsWindow
        settings_window = SettingsWindow(self.config_manager, self)
        if settings_window.exec() == SettingsWindow.DialogCode.Accepted:
            # Reload extraction rules
            self.extraction_rules = self.config_manager.load_extraction_rules()
            self.log_message("Extraction rules updated")
    
    def log_message(self, message: str):
        """Add message to log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def new_session(self):
        """Start a new session."""
        self.data_folder_edit.clear()
        self.subject_list_edit.clear()
        self.target_filename_edit.setText("A_RAPOR_1.jpg")
        self.progress_bar.setValue(0)
        self.progress_label.setText("Ready to start extraction")
        self.log_text.clear()
        self.export_btn.setEnabled(False)
        self.extraction_results = None
        self.log_message("New session started")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About",
            f"{self.app_config['app_title']} v{self.app_config['version']}\n\n"
            f"A user-friendly desktop application for automating\n"
            f"data extraction from various source files and\n"
            f"compiling results into Excel worksheets.\n\n"
            f"Developed for hospital staff to streamline\n"
            f"clinical data extraction workflows.\n\n"
            f"Copyright © 2025 Dr. Skinner\n"
            f"All rights reserved.\n\n"
            f"Licensed under GNU General Public License v3.0.\n"
            f"Third-party libraries: PyQt6, PyMuPDF, pytesseract, pandas, openpyxl"
        )
    
    def check_system_dependencies(self):
        """Check system dependencies and show warnings if needed."""
        from ..core.text_extractor import TextExtractor
        
        # Check Tesseract availability
        tesseract_status = TextExtractor.check_tesseract_availability()
        
        if not tesseract_status['available']:
            self.tesseract_available = False
            self.log_message("⚠️ WARNING: Tesseract OCR not detected!")
            self.log_message(f"Error: {tesseract_status['error']}")
            
            # Show warning dialog
            warning_msg = (
                "⚠️ Tesseract OCR Not Detected\n\n"
                "Image text extraction will not work without Tesseract OCR.\n\n"
                f"Issue: {tesseract_status['error']}\n\n"
                "Installation Instructions:\n"
                "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Install with English and Turkish language packs\n"
                "3. Add to system PATH or restart the application\n\n"
                "PDF extraction will still work normally."
            )
            
            reply = QMessageBox.warning(
                self, "Tesseract OCR Not Found",
                warning_msg,
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore
            )
            
            # Update status bar
            self.status_bar.showMessage("⚠️ Tesseract OCR not available - Image extraction disabled")
            
        else:
            self.tesseract_available = True
            self.log_message(f"✅ Tesseract OCR v{tesseract_status['version']} detected")
            self.log_message(f"Available languages: {', '.join(tesseract_status['languages'])}")
            
            # Warn if Turkish is not available
            if 'tur' not in tesseract_status['languages']:
                self.log_message("⚠️ Turkish language pack not found - consider installing for better results")
                
                QMessageBox.information(
                    self, "Language Pack Recommendation",
                    "Turkish language pack not detected.\n\n"
                    "For better OCR accuracy with Turkish medical documents,\n"
                    "consider reinstalling Tesseract with Turkish language support.\n\n"
                    "English OCR will still work for extraction."
                )
            
            self.status_bar.showMessage("✅ All dependencies available")
    
    def validate_inputs(self) -> bool:
        """Validate user inputs."""
        if not self.data_folder_edit.text():
            QMessageBox.warning(self, "Validation Error", "Please select a data folder.")
            return False
        
        if not self.subject_list_edit.text():
            QMessageBox.warning(self, "Validation Error", "Please select a subject list file.")
            return False
        
        if not self.target_filename_edit.text():
            QMessageBox.warning(self, "Validation Error", "Please enter a target filename.")
            return False
        
        if not os.path.exists(self.data_folder_edit.text()):
            QMessageBox.warning(self, "Validation Error", "Data folder does not exist.")
            return False
        
        if not os.path.exists(self.subject_list_edit.text()):
            QMessageBox.warning(self, "Validation Error", "Subject list file does not exist.")
            return False
        
        # Check if target file is an image and Tesseract is not available
        target_filename = self.target_filename_edit.text().lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif']
        is_image = any(target_filename.endswith(ext) for ext in image_extensions)
        
        if is_image and not self.tesseract_available:
            reply = QMessageBox.question(
                self, "Tesseract OCR Required",
                "The target file appears to be an image, but Tesseract OCR is not available.\n\n"
                "Image text extraction will fail without Tesseract.\n\n"
                "Do you want to proceed anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return False
        
        return True
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.extraction_worker and self.extraction_worker.isRunning():
            reply = QMessageBox.question(
                self, "Exit Application",
                "Extraction is in progress. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.extraction_worker.terminate()
                self.extraction_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
