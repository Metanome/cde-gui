"""
Configuration manager for the Clinical Data Extractor application.
"""

import json
import os
from typing import Dict, List, Any


class ConfigManager:
    """Manages application configuration and extraction rules."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.app_config_path = os.path.join(config_dir, "app_config.json")
        self.rules_config_path = os.path.join(config_dir, "default_rules.json")
        
    def load_app_config(self) -> Dict[str, Any]:
        """Load application configuration."""
        try:
            with open(self.app_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_app_config()
    
    def load_extraction_rules(self) -> List[Dict[str, str]]:
        """Load data extraction rules."""
        try:
            with open(self.rules_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_rules()
    
    def save_extraction_rules(self, rules: List[Dict[str, str]]) -> None:
        """Save data extraction rules."""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.rules_config_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4, ensure_ascii=False)
    
    def _get_default_app_config(self) -> Dict[str, Any]:
        """Get default application configuration."""
        return {
            "app_title": "Clinical Data Extractor (CDE)",
            "version": "1.0.0",
            "organization": "Metanome",
            "window_size": [1000, 700],
            "minimum_window_size": [800, 600],
            "settings_dialog_size": [800, 600],
            "test_pattern_dialog_size": [600, 400],
            "supported_image_formats": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
            "supported_pdf_formats": [".pdf"],
            "tesseract_config": "--psm 6 -l eng",
            "max_workers": 4
        }
    
    def _get_default_rules(self) -> List[Dict[str, str]]:
        """Get default extraction rules from default_rules.json file."""
        try:
            default_rules_path = os.path.join(self.config_dir, 'default_rules.json')
            with open(default_rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # Fallback if file is missing
            return [
                {
                    "name": "Age",
                    "pattern": r"Age\s*:\s*([\d.]+)",
                    "transform": "age_round"
                },
                {
                    "name": "Gender",
                    "pattern": r"Gender\s*:\s*(\w+)",
                    "transform": "gender_turkish"
                },
                {
                    "name": "Date of Test",
                    "pattern": r"(?:Date of Test|Test Date|Date)\s*:\s*([\d\-\/\.]+)",
                    "transform": "none"
                },
                {
                    "name": "Clinician",
                    "pattern": r"(?:Clinician|Doctor|Physician|Dr\.)\s*:?\s*([A-Za-z\s\.]+)",
                    "transform": "none"
                }
            ]
