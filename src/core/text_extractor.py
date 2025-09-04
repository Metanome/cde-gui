"""
Text extraction engine for various file formats.
"""

import os
import sys
import tempfile
import subprocess
from typing import Optional, Dict, Any
from PIL import Image
import pytesseract
import fitz  # PyMuPDF


class TesseractNotFoundError(Exception):
    """Raised when Tesseract OCR is not found or properly installed."""
    pass


class TextExtractor:
    """Handles text extraction from various file formats."""
    
    def __init__(self, tesseract_config: str = "--psm 6 -l eng"):
        """
        Initialize text extractor.
        
        Args:
            tesseract_config: Tesseract OCR configuration
            
        Raises:
            TesseractNotFoundError: If Tesseract is not properly installed
        """
        self.tesseract_config = tesseract_config
        self._validate_tesseract_installation()
    
    def _validate_tesseract_installation(self):
        """
        Validate that Tesseract OCR is properly installed and accessible.
        
        Raises:
            TesseractNotFoundError: If Tesseract is not found or configured properly
        """
        try:
            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract OCR detected: v{version}")
            
            # Try to get available languages
            languages = pytesseract.get_languages()
            print(f"Available OCR languages: {', '.join(languages)}")
            
            # Check if English is available (minimum requirement)
            if 'eng' not in languages:
                raise TesseractNotFoundError(
                    "English language pack not found in Tesseract installation. "
                    "Please reinstall Tesseract with English language support."
                )
            
        except pytesseract.TesseractNotFoundError:
            # Tesseract executable not found
            error_msg = self._get_tesseract_installation_instructions()
            raise TesseractNotFoundError(error_msg)
        
        except Exception as e:
            # Other Tesseract-related errors
            raise TesseractNotFoundError(
                f"Tesseract OCR validation failed: {str(e)}\n\n"
                f"Please ensure Tesseract OCR is properly installed and accessible."
            )
    
    def _get_tesseract_installation_instructions(self) -> str:
        """Get platform-specific Tesseract installation instructions."""
        if sys.platform.startswith('win'):
            return (
                "Tesseract OCR not found!\n\n"
                "Windows Installation Instructions:\n"
                "1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Install with English and Turkish language packs\n"
                "3. Add Tesseract to your system PATH, or\n"
                "4. Set the full path in your application configuration\n\n"
                "Default installation path: C:\\Program Files\\Tesseract-OCR\\"
            )
        elif sys.platform.startswith('darwin'):
            return (
                "Tesseract OCR not found!\n\n"
                "macOS Installation Instructions:\n"
                "1. Install using Homebrew: brew install tesseract\n"
                "2. Or download from: https://github.com/tesseract-ocr/tesseract\n"
                "3. Ensure tesseract is in your PATH"
            )
        else:
            return (
                "Tesseract OCR not found!\n\n"
                "Linux Installation Instructions:\n"
                "1. Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-eng\n"
                "2. CentOS/RHEL: sudo yum install tesseract tesseract-langpack-eng\n"
                "3. Or compile from source: https://github.com/tesseract-ocr/tesseract"
            )
    
    @staticmethod
    def check_tesseract_availability() -> Dict[str, Any]:
        """
        Check Tesseract availability without raising exceptions.
        
        Returns:
            Dictionary with availability status and details
        """
        result = {
            'available': False,
            'version': None,
            'languages': [],
            'error': None,
            'path': None
        }
        
        try:
            # Check if tesseract command is accessible
            result['version'] = str(pytesseract.get_tesseract_version())
            result['languages'] = pytesseract.get_languages()
            result['available'] = True
            
            # Try to get tesseract path
            try:
                result['path'] = pytesseract.pytesseract.tesseract_cmd
            except:
                result['path'] = "Default system path"
                
        except pytesseract.TesseractNotFoundError:
            result['error'] = "Tesseract executable not found in PATH"
        except Exception as e:
            result['error'] = f"Tesseract validation error: {str(e)}"
        
        return result
    
    def extract_text(self, file_path: str, file_type: str) -> Optional[str]:
        """
        Extract text from file based on type.
        
        Args:
            file_path: Path to file
            file_type: Type of file ('image', 'pdf')
            
        Returns:
            Extracted text or None if extraction failed
        """
        try:
            if file_type == 'image':
                return self._extract_from_image(file_path)
            elif file_type == 'pdf':
                return self._extract_from_pdf(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None
    
    def _extract_from_image(self, image_path: str) -> Optional[str]:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text or None
        """
        try:
            # Open and process image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            return text.strip() if text else None
            
        except Exception as e:
            print(f"Error in OCR for {image_path}: {str(e)}")
            return None
    
    def _extract_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None
        """
        try:
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
            print(f"Error extracting PDF text from {pdf_path}: {str(e)}")
            return None
    
    def extract_and_validate(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Extract text and provide validation information.
        
        Args:
            file_path: Path to file
            file_type: Type of file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        result = {
            'file_path': file_path,
            'file_type': file_type,
            'text': None,
            'success': False,
            'error': None,
            'text_length': 0
        }
        
        try:
            text = self.extract_text(file_path, file_type)
            
            if text:
                result['text'] = text
                result['success'] = True
                result['text_length'] = len(text)
            else:
                result['error'] = 'No text extracted'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
