"""
Comprehensive system validation for Clinical Data Extractor.
Checks all dependencies and provides detailed diagnostics for executable packaging.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class SystemValidator:
    """Comprehensive system validation for CDE application."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate_all(self):
        """Run all validation checks."""
        print("=" * 60)
        print("CLINICAL DATA EXTRACTOR - SYSTEM VALIDATION")
        print("=" * 60)
        
        self.check_python_version()
        self.check_python_packages()
        self.check_tesseract_installation()
        self.check_internal_modules()
        self.check_file_permissions()
        self.check_executable_packaging_requirements()
        
        self.print_summary()
        
        return len(self.errors) == 0
    
    def check_python_version(self):
        """Check Python version compatibility."""
        print("\n🐍 PYTHON VERSION CHECK")
        print("-" * 30)
        
        version = sys.version_info
        print(f"Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append("Python 3.8 or higher is required")
            print("❌ Python version too old")
        else:
            self.info.append(f"Python {version.major}.{version.minor}.{version.micro} OK")
            print("✅ Python version compatible")
    
    def check_python_packages(self):
        """Check required Python packages."""
        print("\n📦 PYTHON PACKAGES CHECK")
        print("-" * 30)
        
        required_packages = {
            'PyQt6': 'PyQt6',
            'pytesseract': 'pytesseract',
            'PyMuPDF': 'fitz',
            'openpyxl': 'openpyxl',
            'pandas': 'pandas',
            'Pillow': 'PIL',
            'regex': 'regex'
        }
        
        for package_name, import_name in required_packages.items():
            try:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'Unknown')
                print(f"✅ {package_name}: {version}")
                self.info.append(f"{package_name} v{version} installed")
            except ImportError:
                print(f"❌ {package_name}: Not installed")
                self.errors.append(f"{package_name} package not installed")
    
    def check_tesseract_installation(self):
        """Check Tesseract OCR installation."""
        print("\n🔍 TESSERACT OCR CHECK")
        print("-" * 30)
        
        try:
            # Try to import and test pytesseract
            import pytesseract
            
            # Check if tesseract executable is found
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version: {version}")
            
            # Check available languages
            languages = pytesseract.get_languages()
            print(f"✅ Available languages: {', '.join(languages)}")
            
            # Check critical languages
            if 'eng' not in languages:
                self.errors.append("English language pack missing from Tesseract")
                print("❌ English language pack missing")
            else:
                print("✅ English language pack available")
            
            if 'tur' not in languages:
                self.warnings.append("Turkish language pack not found")
                print("⚠️  Turkish language pack missing (recommended for hospital use)")
            else:
                print("✅ Turkish language pack available")
            
            # Check tesseract path for executable packaging
            tesseract_path = pytesseract.pytesseract.tesseract_cmd
            if tesseract_path == 'tesseract':
                print("ℹ️  Using system PATH for tesseract")
                # Try to find actual path
                actual_path = shutil.which('tesseract')
                if actual_path:
                    print(f"ℹ️  Tesseract found at: {actual_path}")
                    self.info.append(f"Tesseract executable: {actual_path}")
                else:
                    self.warnings.append("Tesseract executable path not explicitly set")
            else:
                print(f"ℹ️  Tesseract path: {tesseract_path}")
                self.info.append(f"Tesseract executable: {tesseract_path}")
            
        except Exception as e:
            print(f"❌ Tesseract not available: {str(e)}")
            self.errors.append(f"Tesseract OCR error: {str(e)}")
    
    def check_internal_modules(self):
        """Check internal application modules."""
        print("\n🔧 INTERNAL MODULES CHECK")
        print("-" * 30)
        
        modules_to_test = [
            ('src.utils.config_manager', 'ConfigManager'),
            ('src.utils.data_transformer', 'DataTransformer'),
            ('src.utils.file_navigator', 'FileSystemNavigator'),
            ('src.core.text_extractor', 'TextExtractor'),
            ('src.core.data_processor', 'DataProcessor'),
            ('src.core.extraction_engine', 'ExtractionEngine'),
            ('src.ui.main_window', 'MainWindow'),
            ('src.ui.settings_window', 'SettingsWindow')
        ]
        
        for module_name, class_name in modules_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                print(f"✅ {module_name}.{class_name}")
                self.info.append(f"Internal module {class_name} OK")
            except ImportError as e:
                print(f"❌ {module_name}: Import error - {str(e)}")
                self.errors.append(f"Internal module import error: {module_name}")
            except AttributeError as e:
                print(f"❌ {module_name}: Class {class_name} not found")
                self.errors.append(f"Internal module class error: {class_name}")
    
    def check_file_permissions(self):
        """Check file system permissions."""
        print("\n📁 FILE PERMISSIONS CHECK")
        print("-" * 30)
        
        # Check config directory
        config_dir = Path("config")
        if config_dir.exists():
            if os.access(config_dir, os.R_OK):
                print("✅ Config directory readable")
            else:
                self.errors.append("Config directory not readable")
                print("❌ Config directory not readable")
            
            if os.access(config_dir, os.W_OK):
                print("✅ Config directory writable")
            else:
                self.warnings.append("Config directory not writable")
                print("⚠️  Config directory not writable")
        else:
            self.warnings.append("Config directory not found")
            print("⚠️  Config directory not found")
        
        # Check demo directory
        demo_dir = Path("demo")
        if demo_dir.exists():
            if os.access(demo_dir, os.R_OK):
                print("✅ Demo directory readable")
            else:
                self.warnings.append("Demo directory not readable")
                print("⚠️  Demo directory not readable")
        
        # Test write permissions in current directory
        try:
            test_file = Path("test_write_permission.tmp")
            test_file.write_text("test")
            test_file.unlink()
            print("✅ Current directory writable")
        except Exception:
            self.errors.append("Current directory not writable")
            print("❌ Current directory not writable")
    
    def check_executable_packaging_requirements(self):
        """Check requirements for creating executable packages."""
        print("\n📦 EXECUTABLE PACKAGING CHECK")
        print("-" * 30)
        
        # Check for PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller available: v{PyInstaller.__version__}")
            self.info.append("PyInstaller available for executable creation")
        except ImportError:
            print("ℹ️  PyInstaller not installed (optional for executable creation)")
            print("   Install with: pip install pyinstaller")
        
        # Check for auto-py-to-exe (GUI for PyInstaller)
        try:
            import auto_py_to_exe
            print("✅ auto-py-to-exe available (GUI wrapper for PyInstaller)")
        except ImportError:
            print("ℹ️  auto-py-to-exe not installed (optional GUI for PyInstaller)")
            print("   Install with: pip install auto-py-to-exe")
        
        # Check critical files for packaging
        critical_files = [
            "main.py",
            "requirements.txt",
            "config/app_config.json",
            "config/default_rules.json"
        ]
        
        for file_path in critical_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} missing")
                self.errors.append(f"Critical file missing: {file_path}")
        
        # Platform-specific checks
        if sys.platform.startswith('win'):
            print("ℹ️  Windows platform detected")
            print("ℹ️  For executable: ensure Tesseract is bundled or installed on target systems")
            self.info.append("Windows executable packaging possible")
        elif sys.platform.startswith('darwin'):
            print("ℹ️  macOS platform detected")
            print("ℹ️  For .app bundle: use PyInstaller with --windowed option")
            self.info.append("macOS app bundle packaging possible")
        else:
            print("ℹ️  Linux platform detected")
            print("ℹ️  For AppImage: consider using additional tools")
            self.info.append("Linux executable packaging possible")
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.info:
            print(f"\n✅ INFO ({len(self.info)}):")
            for info in self.info:
                print(f"   • {info}")
        
        print("\n" + "=" * 60)
        
        if not self.errors:
            print("🎉 ALL CHECKS PASSED - SYSTEM READY FOR PRODUCTION!")
            print("\nNext steps:")
            print("1. Run application: python main.py")
            print("2. Create executable: pyinstaller main.py --windowed")
            print("3. Test with sample data in demo/ folder")
        else:
            print("❌ SYSTEM NOT READY - PLEASE FIX ERRORS ABOVE")
            print("\nRecommended actions:")
            print("1. Install missing packages: pip install -r requirements.txt")
            print("2. Install Tesseract OCR with language packs")
            print("3. Fix file permissions issues")
        
        print("=" * 60)


def main():
    """Run system validation."""
    validator = SystemValidator()
    success = validator.validate_all()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
