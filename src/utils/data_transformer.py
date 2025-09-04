"""
Data transformation utilities for the Clinical Data Extractor.
"""

import re
import math
from typing import Any, Optional


class DataTransformer:
    """Handles data transformations based on extraction rules."""
    
    @staticmethod
    def transform_value(value: str, transform_type: str) -> Any:
        """
        Apply transformation to extracted value.
        
        Args:
            value: Raw extracted value
            transform_type: Type of transformation to apply
            
        Returns:
            Transformed value
        """
        if transform_type == "age_round":
            return DataTransformer.round_age(value)
        elif transform_type == "gender_turkish":
            return DataTransformer.map_turkish_gender(value)
        elif transform_type == "none" or not transform_type:
            return value.strip() if isinstance(value, str) else value
        else:
            return value
    
    @staticmethod
    def round_age(age_str: str) -> Optional[int]:
        """
        Round age according to specific logic: round up only if decimal > 0.50.
        
        Args:
            age_str: Age as string (e.g., "25.7", "30.2")
            
        Returns:
            Rounded age as integer
        """
        try:
            age_float = float(age_str.strip())
            decimal_part = age_float - int(age_float)
            
            if decimal_part > 0.50:
                return math.ceil(age_float)
            else:
                return int(age_float)
                
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def map_turkish_gender(gender_str: str) -> Optional[str]:
        """
        Map Turkish gender terms to English.
        
        Args:
            gender_str: Gender string in Turkish
            
        Returns:
            Mapped gender string
        """
        gender_clean = gender_str.strip().upper()
        
        female_terms = ["BAYAN", "K", "KADIN", "F", "FEMALE"]
        male_terms = ["BAY", "E", "ERKEK", "M", "MALE"]
        
        if gender_clean in female_terms:
            return "Female"
        elif gender_clean in male_terms:
            return "Male"
        else:
            return gender_str.strip()  # Return original if no mapping found
    
    @staticmethod
    def extract_with_pattern(text: str, pattern: str) -> Optional[str]:
        """
        Extract data using regex pattern.
        
        Args:
            text: Text to search in
            pattern: Regex pattern with capture group
            
        Returns:
            Extracted value or None
        """
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match and match.groups():
                return match.group(1).strip()
            return None
        except re.error:
            return None
