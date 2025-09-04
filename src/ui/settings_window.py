"""
Settings window for managing data extraction rules.
"""

import json
import re
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGroupBox, QTextEdit, QSplitter,
    QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..utils.config_manager import ConfigManager


class RuleEditDialog(QDialog):
    """Dialog for adding/editing extraction rules."""
    
    def __init__(self, rule: Optional[Dict[str, str]] = None, parent=None):
        super().__init__(parent)
        self.rule = rule or {}
        self.init_ui()
        self.populate_fields()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Edit Extraction Rule")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Rule configuration
        config_group = QGroupBox("Rule Configuration")
        config_layout = QGridLayout(config_group)
        
        # Field name
        config_layout.addWidget(QLabel("Field Name:"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Age, Gender, Test Score")
        config_layout.addWidget(self.name_edit, 0, 1)
        
        # Pattern
        config_layout.addWidget(QLabel("Search Pattern:"), 1, 0)
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText(r"e.g., Age\s*:\s*([\d.]+)")
        config_layout.addWidget(self.pattern_edit, 1, 1)
        
        # Transform
        config_layout.addWidget(QLabel("Transformation:"), 2, 0)
        self.transform_combo = QComboBox()
        self.transform_combo.addItems([
            "none", "age_round", "gender_turkish"
        ])
        config_layout.addWidget(self.transform_combo, 2, 1)
        
        layout.addWidget(config_group)
        
        # Pattern help
        help_group = QGroupBox("Pattern Help")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QTextEdit()
        help_text.setMaximumHeight(120)
        help_text.setReadOnly(True)
        help_text.setPlainText(
            "Regex Pattern Examples:\n"
            "• Age\\s*:\\s*([\\d.]+) - Matches 'Age: 25.5'\n"
            "• Gender\\s*:\\s*(\\w+) - Matches 'Gender: Male'\n"
            "• (\\d+)\\s*years? - Matches '25 years' or '30 year'\n"
            "• Score\\s*[=:]\\s*([\\d.]+) - Matches 'Score = 85.2'\n\n"
            "Use parentheses () to capture the value you want to extract."
        )
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        
        # Transformation help
        transform_help_group = QGroupBox("Transformation Types")
        transform_help_layout = QVBoxLayout(transform_help_group)
        
        transform_help_text = QTextEdit()
        transform_help_text.setMaximumHeight(80)
        transform_help_text.setReadOnly(True)
        transform_help_text.setPlainText(
            "• none - No transformation applied\n"
            "• age_round - Round age (up only if decimal > 0.50)\n"
            "• gender_turkish - Map Turkish gender terms to English"
        )
        transform_help_layout.addWidget(transform_help_text)
        
        layout.addWidget(transform_help_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test Pattern")
        self.test_btn.clicked.connect(self.test_pattern)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_rule)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def populate_fields(self):
        """Populate fields with existing rule data."""
        if self.rule:
            self.name_edit.setText(self.rule.get('name', ''))
            self.pattern_edit.setText(self.rule.get('pattern', ''))
            
            transform = self.rule.get('transform', 'none')
            index = self.transform_combo.findText(transform)
            if index >= 0:
                self.transform_combo.setCurrentIndex(index)
    
    def test_pattern(self):
        """Test the regex pattern."""
        pattern = self.pattern_edit.text().strip()
        if not pattern:
            QMessageBox.warning(self, "Test Pattern", "Please enter a pattern to test.")
            return
        
        # Create a test dialog
        test_dialog = PatternTestDialog(pattern, self)
        test_dialog.exec()
    
    def save_rule(self):
        """Save the rule."""
        name = self.name_edit.text().strip()
        pattern = self.pattern_edit.text().strip()
        transform = self.transform_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a field name.")
            return
        
        if not pattern:
            QMessageBox.warning(self, "Validation Error", "Please enter a search pattern.")
            return
        
        # Test regex validity
        try:
            re.compile(pattern)
        except re.error as e:
            QMessageBox.warning(self, "Pattern Error", f"Invalid regex pattern:\n{str(e)}")
            return
        
        self.rule = {
            'name': name,
            'pattern': pattern,
            'transform': transform
        }
        
        self.accept()
    
    def get_rule(self) -> Dict[str, str]:
        """Get the configured rule."""
        return self.rule


class PatternTestDialog(QDialog):
    """Dialog for testing regex patterns."""
    
    def __init__(self, pattern: str, parent=None):
        super().__init__(parent)
        self.pattern = pattern
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Test Regex Pattern")
        self.setModal(True)
        # Use default size for pattern test dialog
        self.resize(600, 400)
        
        # Apply consistent dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Pattern display
        pattern_label = QLabel(f"Pattern: {self.pattern}")
        pattern_label.setStyleSheet("""
            font-weight: bold; 
            padding: 8px;
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #ffffff;
        """)
        layout.addWidget(pattern_label)
        
        # Test text input
        layout.addWidget(QLabel("Test Text:"))
        self.test_text = QTextEdit()
        self.test_text.setPlaceholderText("Enter sample text to test the pattern against...")
        self.test_text.setMaximumHeight(150)
        self.test_text.setStyleSheet("""
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
            font-family: Consolas, monospace;
        """)
        layout.addWidget(self.test_text)
        
        # Test button
        test_btn = QPushButton("Test Pattern")
        test_btn.clicked.connect(self.run_test)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(test_btn)
        
        # Results
        layout.addWidget(QLabel("Results:"))
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 5px;
            font-family: Consolas, monospace;
        """)
        layout.addWidget(self.results_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        layout.addWidget(close_btn)
    
    def run_test(self):
        """Run pattern test."""
        test_text = self.test_text.toPlainText()
        if not test_text.strip():
            self.results_text.setPlainText("Please enter test text.")
            return
        
        try:
            matches = list(re.finditer(self.pattern, test_text, re.IGNORECASE | re.MULTILINE))
            
            if matches:
                results = f"Found {len(matches)} match(es):\n\n"
                for i, match in enumerate(matches, 1):
                    results += f"Match {i}:\n"
                    results += f"  Full match: '{match.group(0)}'\n"
                    if match.groups():
                        for j, group in enumerate(match.groups(), 1):
                            results += f"  Group {j}: '{group}'\n"
                    results += f"  Position: {match.start()}-{match.end()}\n\n"
            else:
                results = "No matches found."
            
            self.results_text.setPlainText(results)
            
        except re.error as e:
            self.results_text.setPlainText(f"Regex error: {str(e)}")
    
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


class SettingsWindow(QDialog):
    """Main settings window for managing extraction rules."""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.rules = self.config_manager.load_extraction_rules()
        self.init_ui()
        self.populate_rules_table()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Manage Extraction Rules")
        self.setModal(True)
        
        # Get app config for window sizing
        app_config = self.config_manager.load_app_config()
        dialog_size = app_config.get('settings_dialog_size', [800, 600])
        self.resize(*dialog_size)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Data Extraction Rules Configuration")
        header_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Rules table
        self.create_rules_section(layout)
        
        # Buttons
        self.create_button_section(layout)
    
    def create_rules_section(self, layout: QVBoxLayout):
        """Create rules management section."""
        rules_group = QGroupBox("Extraction Rules")
        rules_layout = QVBoxLayout(rules_group)
        
        # Table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Field Name", "Pattern", "Transform"])
        
        # Set column widths
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set minimum column widths to prevent truncation
        self.rules_table.setColumnWidth(0, 120)  # Field Name
        self.rules_table.setColumnWidth(1, 300)  # Pattern (minimum width)
        self.rules_table.setColumnWidth(2, 120)  # Transform
        
        # Enable text wrapping for long patterns
        self.rules_table.setWordWrap(True)
        self.rules_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.setAlternatingRowColors(True)
        self.rules_table.doubleClicked.connect(self.edit_rule)
        
        rules_layout.addWidget(self.rules_table)
        
        # Rule management buttons
        rule_buttons_layout = QHBoxLayout()
        
        self.add_rule_btn = QPushButton("Add Rule")
        self.add_rule_btn.clicked.connect(self.add_rule)
        self.add_rule_btn.setStyleSheet(self._get_button_style("#27ae60"))
        rule_buttons_layout.addWidget(self.add_rule_btn)
        
        self.edit_rule_btn = QPushButton("Edit Rule")
        self.edit_rule_btn.clicked.connect(self.edit_rule)
        self.edit_rule_btn.setStyleSheet(self._get_button_style("#3498db"))
        rule_buttons_layout.addWidget(self.edit_rule_btn)
        
        self.delete_rule_btn = QPushButton("Delete Rule")
        self.delete_rule_btn.clicked.connect(self.delete_rule)
        self.delete_rule_btn.setStyleSheet(self._get_button_style("#e74c3c"))
        rule_buttons_layout.addWidget(self.delete_rule_btn)
        
        rule_buttons_layout.addStretch()
        
        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.move_rule_up)
        self.move_up_btn.setStyleSheet(self._get_button_style("#95a5a6"))
        rule_buttons_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.move_rule_down)
        self.move_down_btn.setStyleSheet(self._get_button_style("#95a5a6"))
        rule_buttons_layout.addWidget(self.move_down_btn)
        
        rules_layout.addLayout(rule_buttons_layout)
        
        layout.addWidget(rules_group)
    
    def create_button_section(self, layout: QVBoxLayout):
        """Create main button section."""
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.reset_btn.setStyleSheet(self._get_button_style("#f39c12"))
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet(self._get_button_style("#95a5a6"))
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setStyleSheet(self._get_button_style("#27ae60"))
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _get_button_style(self, color: str) -> str:
        """Get button styling."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def populate_rules_table(self):
        """Populate the rules table."""
        self.rules_table.setRowCount(len(self.rules))
        
        for row, rule in enumerate(self.rules):
            # Field name
            self.rules_table.setItem(row, 0, QTableWidgetItem(rule.get('name', '')))
            
            # Pattern (truncate if too long)
            pattern = rule.get('pattern', '')
            if len(pattern) > 50:
                pattern = pattern[:47] + "..."
            self.rules_table.setItem(row, 1, QTableWidgetItem(pattern))
            
            # Transform
            self.rules_table.setItem(row, 2, QTableWidgetItem(rule.get('transform', 'none')))
    
    def add_rule(self):
        """Add a new rule."""
        dialog = RuleEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.rules.append(rule)
            self.populate_rules_table()
    
    def edit_rule(self):
        """Edit selected rule."""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Edit Rule", "Please select a rule to edit.")
            return
        
        rule = self.rules[current_row]
        dialog = RuleEditDialog(rule, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_rule = dialog.get_rule()
            self.rules[current_row] = updated_rule
            self.populate_rules_table()
    
    def delete_rule(self):
        """Delete selected rule."""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Delete Rule", "Please select a rule to delete.")
            return
        
        rule = self.rules[current_row]
        reply = QMessageBox.question(
            self, "Delete Rule",
            f"Are you sure you want to delete the rule '{rule.get('name', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.rules[current_row]
            self.populate_rules_table()
    
    def move_rule_up(self):
        """Move selected rule up."""
        current_row = self.rules_table.currentRow()
        if current_row <= 0:
            return
        
        # Swap rules
        self.rules[current_row], self.rules[current_row - 1] = \
            self.rules[current_row - 1], self.rules[current_row]
        
        self.populate_rules_table()
        self.rules_table.setCurrentCell(current_row - 1, 0)
    
    def move_rule_down(self):
        """Move selected rule down."""
        current_row = self.rules_table.currentRow()
        if current_row < 0 or current_row >= len(self.rules) - 1:
            return
        
        # Swap rules
        self.rules[current_row], self.rules[current_row + 1] = \
            self.rules[current_row + 1], self.rules[current_row]
        
        self.populate_rules_table()
        self.rules_table.setCurrentCell(current_row + 1, 0)
    
    def reset_to_defaults(self):
        """Reset rules to default configuration."""
        reply = QMessageBox.question(
            self, "Reset to Defaults",
            "Are you sure you want to reset all rules to defaults? This will remove all custom rules.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.rules = self.config_manager._get_default_rules()
            self.populate_rules_table()
    
    def save_changes(self):
        """Save changes and close."""
        # Validate rules
        errors = []
        for i, rule in enumerate(self.rules):
            if not rule.get('name'):
                errors.append(f"Rule {i + 1}: Missing field name")
            if not rule.get('pattern'):
                errors.append(f"Rule {i + 1}: Missing pattern")
            
            # Test regex
            try:
                re.compile(rule.get('pattern', ''))
            except re.error as e:
                errors.append(f"Rule {i + 1}: Invalid pattern - {str(e)}")
        
        if errors:
            QMessageBox.critical(
                self, "Validation Errors",
                "Please fix the following errors:\n\n" + "\n".join(errors)
            )
            return
        
        # Save rules
        try:
            self.config_manager.save_extraction_rules(self.rules)
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Save Error",
                f"Failed to save rules:\n{str(e)}"
            )
