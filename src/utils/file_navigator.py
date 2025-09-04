"""
File system utilities for the Clinical Data Extractor.
"""

import os
import re
from typing import List, Tuple, Optional, Dict
from pathlib import Path


class FileSystemNavigator:
    """Handles file system navigation and subject folder parsing."""
    
    def __init__(self, root_folder: str):
        """
        Initialize navigator with root folder.
        
        Args:
            root_folder: Root directory to search
        """
        self.root_folder = root_folder
    
    def get_subject_folders(self, subject_list: List[str]) -> List[Tuple[str, str, str]]:
        """
        Get subject folders that match the subject list.
        
        Args:
            subject_list: List of subject IDs to process
            
        Returns:
            List of tuples (subject_id, patient_name, folder_path)
        """
        subject_folders = []
        
        if not os.path.exists(self.root_folder):
            return subject_folders
        
        for item in os.listdir(self.root_folder):
            folder_path = os.path.join(self.root_folder, item)
            
            if os.path.isdir(folder_path):
                subject_id, patient_name = self.parse_folder_name(item)
                
                if subject_id and subject_id in subject_list:
                    subject_folders.append((subject_id, patient_name, folder_path))
        
        return subject_folders
    
    def parse_folder_name(self, folder_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse subject ID and patient name from folder name.
        Expected format: SubjectID_PatientName
        Handles multiple spaces in names (e.g., "001_Name  Surname")
        
        Args:
            folder_name: Name of the folder
            
        Returns:
            Tuple of (subject_id, patient_name)
        """
        # Pattern: SubjectID_PatientName
        if '_' in folder_name:
            parts = folder_name.split('_', 1)
            subject_id = parts[0].strip()
            # Normalize multiple spaces in patient name to single spaces
            patient_name = ' '.join(parts[1].split()) if len(parts) > 1 else ""
            return subject_id, patient_name
        else:
            # If no underscore, treat entire name as subject ID
            return folder_name.strip(), ""
    
    def find_target_files(self, subject_folder: str, target_filename: str) -> List[str]:
        """
        Find target files in subject subfolders.
        Structure: SubjectFolder > [1, 2, 3...n] > DataFiles
        
        Args:
            subject_folder: Path to subject folder
            target_filename: Name of target file to find
            
        Returns:
            List of paths to found target files
        """
        target_files = []
        
        if not os.path.exists(subject_folder):
            return target_files
        
        # Look in numbered subfolders
        for item in os.listdir(subject_folder):
            subfolder_path = os.path.join(subject_folder, item)
            
            if os.path.isdir(subfolder_path):
                # Check if folder name is numeric (1, 2, 3, etc.)
                if item.isdigit():
                    target_file_path = os.path.join(subfolder_path, target_filename)
                    if os.path.exists(target_file_path):
                        target_files.append(target_file_path)
        
        return target_files
    
    def load_subject_list(self, subject_list_file: str) -> List[str]:
        """
        Load subject list from text file.
        
        Args:
            subject_list_file: Path to text file containing subject IDs
            
        Returns:
            List of subject IDs
        """
        subject_list = []
        
        try:
            with open(subject_list_file, 'r', encoding='utf-8') as f:
                for line in f:
                    subject_id = line.strip()
                    if subject_id:  # Skip empty lines
                        subject_list.append(subject_id)
        except FileNotFoundError:
            pass
        
        return subject_list
    
    def get_file_type(self, file_path: str) -> str:
        """
        Get file type based on extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            File type ('image', 'pdf', 'unknown')
        """
        ext = Path(file_path).suffix.lower()
        
        image_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif']
        pdf_formats = ['.pdf']
        
        if ext in image_formats:
            return 'image'
        elif ext in pdf_formats:
            return 'pdf'
        else:
            return 'unknown'
