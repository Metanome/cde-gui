# Clinical Data Extractor (CDE) - Installation Guide

## Prerequisites

Before running the Clinical Data Extractor, ensure you have the following installed:

### 1. Python 3.8 or higher
Download from [python.org](https://www.python.org/downloads/)

### 2. Tesseract OCR (for image text extraction)
- **Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **After installation**, add Tesseract to your system PATH or note the installation directory

### 3. Git (optional, for cloning the repository)
Download from [git-scm.com](https://git-scm.com/)

## Installation Steps

### Step 1: Clone or Download the Project
```bash
git clone <repository-url>
cd cde-gui
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Tesseract (if needed)
If Tesseract is not in your system PATH, you may need to configure the path in the application or set the environment variable:

**Windows Example:**
```bash
set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

### Step 6: Test the Installation
```bash
python test_system.py
```

This will verify that all dependencies are properly installed and the system is ready.

### Step 7: Run the Application
```bash
python main.py
```

## Troubleshooting

### Common Issues

1. **PyQt6 Installation Issues**
   - Try: `pip install PyQt6 --no-cache-dir`
   - On some systems: `pip install PyQt6-Qt6`

2. **Tesseract Not Found**
   - Ensure Tesseract is installed and in PATH
   - Set TESSDATA_PREFIX environment variable
   - In the app config, update the tesseract path if needed

3. **PDF Extraction Issues**
   - Ensure PyMuPDF is properly installed: `pip install PyMuPDF`

4. **Permission Issues on Windows**
   - Run command prompt as Administrator
   - Or use `pip install --user <package>`

### Package Versions
- PyQt6 >= 6.5.0
- pytesseract >= 0.3.10
- PyMuPDF >= 1.23.0
- openpyxl >= 3.1.0
- pandas >= 2.0.0
- Pillow >= 10.0.0

## Usage

1. Launch the application: `python main.py`
2. Select your data folder (root network folder)
3. Select your subject list .txt file
4. Configure the target filename (e.g., "A_RAPOR_1.jpg")
5. Click "Manage Rules" to configure extraction patterns
6. Click "Start Extraction" to begin processing
7. Export results to Excel when complete

## Configuration

The application stores configuration in the `config/` directory:
- `app_config.json` - Application settings
- `default_rules.json` - Data extraction rules

You can modify these files directly or use the built-in settings interface.

## Support

For issues or questions:
1. Check the Activity Log in the application
2. Run the test script to verify installation
3. Review the console output for error messages
4. Ensure all file paths and permissions are correct
