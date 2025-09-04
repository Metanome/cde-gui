"""
Main extraction engine that coordinates the data extraction process.
"""

import os
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..utils.file_navigator import FileSystemNavigator
from .text_extractor import TextExtractor, TesseractNotFoundError
from .data_processor import DataProcessor


class ExtractionEngine:
    """Main engine for coordinating the data extraction process."""
    
    def __init__(self, config: Dict[str, Any], extraction_rules: List[Dict[str, str]]):
        """
        Initialize extraction engine.
        
        Args:
            config: Application configuration
            extraction_rules: List of extraction rules
            
        Raises:
            TesseractNotFoundError: If Tesseract is required but not available
        """
        self.config = config
        self.extraction_rules = extraction_rules
        self.data_processor = DataProcessor(extraction_rules)
        self.max_workers = config.get('max_workers', 4)
        
        # Initialize text extractor with error handling
        try:
            self.text_extractor = TextExtractor(config.get('tesseract_config', '--psm 6 -l eng'))
            self.tesseract_available = True
        except TesseractNotFoundError as e:
            print(f"Warning: {str(e)}")
            self.text_extractor = None
            self.tesseract_available = False
    
    def extract_data(
        self, 
        root_folder: str, 
        subject_list_file: str, 
        target_filename: str,
        progress_callback: Callable[[int, str], None] = None
    ) -> Dict[str, Any]:
        """
        Main extraction method.
        
        Args:
            root_folder: Root directory to search
            subject_list_file: Path to subject list file
            target_filename: Target filename to extract from
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with extraction results and statistics
        """
        results = {
            'success': False,
            'data': [],
            'total_subjects': 0,
            'processed_subjects': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'errors': []
        }
        
        try:
            # Initialize file navigator
            navigator = FileSystemNavigator(root_folder)
            
            # Load subject list
            if progress_callback:
                progress_callback(10, "Loading subject list...")
            
            subject_list = navigator.load_subject_list(subject_list_file)
            if not subject_list:
                results['errors'].append("No subjects found in subject list file")
                return results
            
            # Get subject folders
            if progress_callback:
                progress_callback(20, "Finding subject folders...")
            
            subject_folders = navigator.get_subject_folders(subject_list)
            results['total_subjects'] = len(subject_folders)
            
            # Check for missing subjects
            found_subject_ids = {folder[0] for folder in subject_folders}
            missing_subjects = [sid for sid in subject_list if sid not in found_subject_ids]
            
            if missing_subjects:
                results['missing_subjects'] = missing_subjects
                missing_count = len(missing_subjects)
                results['warnings'] = results.get('warnings', [])
                results['warnings'].append(f"Missing {missing_count} subject folders: {', '.join(missing_subjects)}")
            
            if not subject_folders:
                if missing_subjects:
                    results['errors'].append(f"No subject folders found. Missing: {', '.join(missing_subjects)}")
                else:
                    results['errors'].append("No subject folders found matching the subject list")
                return results
            
            # Process subjects
            if progress_callback:
                progress_callback(30, f"Processing {len(subject_folders)} subjects...")
            
            extraction_data = self._process_subjects(
                subject_folders, 
                target_filename, 
                navigator,
                progress_callback
            )
            
            results['data'] = extraction_data
            results['processed_subjects'] = len(extraction_data)
            
            # Count successful extractions based on whether any extraction rules found data
            successful_count = 0
            for item in extraction_data:
                # Check if any extraction rule found data (excluding subject_id and name)
                has_extracted_data = any(
                    key not in ['subject_id', 'name'] and value and str(value).strip()
                    for key, value in item.items()
                )
                if has_extracted_data:
                    successful_count += 1
            
            results['successful_extractions'] = successful_count
            results['failed_extractions'] = results['processed_subjects'] - results['successful_extractions']
            
            if progress_callback:
                progress_callback(90, "Processing extraction data...")
            
            results['success'] = True
            
        except Exception as e:
            results['errors'].append(f"Extraction error: {str(e)}")
        
        if progress_callback:
            progress_callback(100, "Extraction completed")
        
        return results
    
    def _process_subjects(
        self, 
        subject_folders: List[tuple], 
        target_filename: str, 
        navigator: FileSystemNavigator,
        progress_callback: Callable[[int, str], None] = None
    ) -> List[Dict[str, Any]]:
        """Process all subject folders and extract data."""
        extraction_data = []
        total_subjects = len(subject_folders)
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_subject = {
                executor.submit(
                    self._process_single_subject, 
                    subject_id, 
                    patient_name, 
                    folder_path, 
                    target_filename, 
                    navigator
                ): (subject_id, patient_name)
                for subject_id, patient_name, folder_path in subject_folders
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_subject):
                completed += 1
                subject_id, patient_name = future_to_subject[future]
                
                try:
                    result = future.result()
                    extraction_data.append(result)
                    
                    if progress_callback:
                        progress = 30 + int((completed / total_subjects) * 50)
                        status = f"Processed {subject_id} ({completed}/{total_subjects})"
                        progress_callback(progress, status)
                        
                except Exception as e:
                    # Handle individual subject processing errors
                    error_result = {
                        'subject_id': subject_id,
                        'patient_name': patient_name,
                        'file_path': '',
                        'extracted_text': None,
                        'extraction_status': 'Failed',
                        'error': str(e)
                    }
                    extraction_data.append(error_result)
        
        return extraction_data
    
    def _process_single_subject(
        self, 
        subject_id: str, 
        patient_name: str, 
        folder_path: str, 
        target_filename: str, 
        navigator: FileSystemNavigator
    ) -> Dict[str, Any]:
        """Process a single subject folder."""
        result = {
            'subject_id': subject_id,
            'patient_name': patient_name,
            'file_path': '',
            'extracted_text': None,
            'extraction_status': 'Failed',
            'error': None
        }
        
        try:
            # Find target files
            target_files = navigator.find_target_files(folder_path, target_filename)
            
            if not target_files:
                result['error'] = f"Target file '{target_filename}' not found"
                return result
            
            # Process the first found file (or could be modified to process all)
            target_file = target_files[0]
            result['file_path'] = target_file
            
            # Determine file type
            file_type = navigator.get_file_type(target_file)
            
            if file_type == 'unknown':
                result['error'] = f"Unsupported file type: {target_file}"
                return result
            
            # Check if Tesseract is required but not available
            if file_type == 'image' and not self.tesseract_available:
                result['error'] = "Tesseract OCR not available for image text extraction"
                return result
            
            # Extract text
            if file_type == 'image' and self.text_extractor:
                extracted_text = self.text_extractor.extract_text(target_file, file_type)
            elif file_type == 'pdf':
                # For PDF, we can use a fallback text extractor that doesn't require Tesseract
                if self.text_extractor:
                    extracted_text = self.text_extractor.extract_text(target_file, file_type)
                else:
                    # Fallback PDF extraction without TextExtractor instance
                    extracted_text = self._extract_pdf_fallback(target_file)
            else:
                extracted_text = None
            
            if extracted_text:
                result['extracted_text'] = extracted_text
                result['extraction_status'] = 'Success'
            else:
                result['error'] = "Failed to extract text from file"
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _extract_pdf_fallback(self, pdf_path: str) -> str:
        """
        Fallback PDF text extraction that doesn't require Tesseract.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None
        """
        try:
            import fitz  # PyMuPDF
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_content.append(text)
            
            doc.close()
            
            # Combine all text
            full_text = '\n'.join(text_content)
            return full_text.strip() if full_text else None
            
        except Exception as e:
            print(f"PDF extraction fallback failed for {pdf_path}: {str(e)}")
            return None
    
    def generate_excel_report(self, extraction_results: Dict[str, Any], output_path: str) -> bool:
        """
        Generate Excel report from extraction results.
        
        Args:
            extraction_results: Results from extract_data method
            output_path: Path for output Excel file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Process the raw data
            processed_df = self.data_processor.process_extracted_data(
                extraction_results.get('data', [])
            )
            
            # Export to Excel
            return self.data_processor.export_to_excel(processed_df, output_path)
            
        except Exception as e:
            print(f"Error generating Excel report: {str(e)}")
            return False
