# Clinical Data Extractor (CDE)

A desktop application for automated data extraction from various source files (images, PDFs) and compilation into Excel worksheets.

## Objective

A comprehensive solution for healthcare organizations to automate data extraction from various source files and compile results into properly formatted Excel worksheets. The application provides an intuitive interface that enables users to configure extraction parameters without source code modifications.

## Key Features

- **PyQt6 Interface** - Responsive user interface with real-time processing feedback
- **Configurable Extraction Rules** - User-defined patterns and data transformations
- **Multi-format Support** - Image processing via OCR and PDF text extraction
- **Excel Output Generation** - Automated column generation based on extraction rules
- **Progress Monitoring** - Status tracking, progress indicators, and detailed activity logging
- **Localization Support** - Built-in support for Turkish language data mapping
- **Concurrent Processing** - Multi-threaded extraction for enhanced performance
- **File Structure Navigation** - Automated handling of nested directory structures

## Screenshots
| Main Interface | Manage Rule Creation |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/5c011d28-62ad-4885-8853-b382bf8b1f37" alt="Screenshot1" width="400"/> | <img src="https://github.com/user-attachments/assets/6ddf506f-916e-44c2-8b48-66e59e3e85b7" alt="Screenshot2" width="400"/> |
| **Edit Rule Creation** | **Test Rule Creation** |
| <img src="https://github.com/user-attachments/assets/c0b232d4-0c4e-4818-a7c4-3788a41cdd4b" alt="Screenshot3" width="300"/> | <img src="https://github.com/user-attachments/assets/f0064a77-6fd2-474d-8fee-c83bfc9d8883" alt="Screenshot4" width="350"/> |

## Project Structure

```
cde-gui/
├── src/
│   ├── ui/                     # PyQt6 user interface components
│   │   ├── main_window.py      # Main application window
│   │   └── settings_window.py  # Rules management window
│   ├── core/                   # Core data processing logic
│   │   ├── text_extractor.py   # OCR and PDF text extraction
│   │   ├── data_processor.py   # Data processing and Excel generation
│   │   └── extraction_engine.py # Main extraction coordinator
│   └── utils/                  # Utility functions and helpers
│       ├── config_manager.py   # Configuration management
│       ├── data_transformer.py # Data transformation logic
│       └── file_navigator.py   # File system navigation
├── config/                     # Configuration files
│   ├── app_config.json        # Application settings
│   └── default_rules.json     # Default extraction rules
├── main.py                    # Application entry point
└── requirements.txt          # Python dependencies
```

## Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Tesseract OCR Setup
- **Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- Add installation directory to system PATH

### Application Launch
```bash
python main.py
```

## Usage Guide

### Workflow

1. **Application Launch**
   ```bash
   python main.py
   ```

2. **Input Configuration**
   - Select root data directory using "Browse" button
   - Specify subject list file (.txt format) containing subject identifiers

3. **Target File Configuration**
   - Define target filename pattern (e.g., `A_RAPOR_1.jpg`, `summary.pdf`)

4. **Extraction Rules Management**
   - Access "Manage Rules" interface to configure data extraction patterns
   - Configure, test, and validate regex patterns
   - Apply data transformation rules as required

5. **Processing Execution**
   - Initiate extraction process via "Start Extraction"
   - Monitor real-time progress and status updates
   - Review detailed processing logs

6. **Results Export**
   - Generate Excel output using "Export to Excel"
   - Specify output location and filename

### Directory Structure Requirements

```
Root Folder/
├── SubjectID_PatientName/
│   ├── 1/
│   │   ├── target_file.jpg
│   │   └── other_files...
│   ├── 2/
│   │   └── target_file.jpg
│   └── ...
├── AnotherSubject_Name/
│   └── 1/
│       └── target_file.jpg
└── ...
```

### Subject List Format

Subject identifier file format (one ID per line):
```
001
002
003
SUBJ_123
```

## Configuration

### Extraction Rules

Extraction rules are configured through the management interface and consist of:

- **Field Name**: Output column identifier (e.g., "Age", "Gender")
- **Search Pattern**: Regular expression with capture group (e.g., `Age\s*:\s*([\d.]+)`)
- **Transformation**: Data transformation options:
  - `none` - No transformation applied
  - `age_round` - Age rounding (up if decimal > 0.50)
  - `gender_turkish` - Turkish-to-English gender term mapping

### Example Rules

```json
[
    {
        "name": "Age",
        "pattern": "Age\\s*:\\s*([\\d.]+)",
        "transform": "age_round"
    },
    {
        "name": "Gender",
        "pattern": "Gender\\s*:\\s*(\\w+)",
        "transform": "gender_turkish"
    },
    {
        "name": "Date of Test",
        "pattern": "(?:Date of Test|Test Date|Date)\\s*:\\s*([\\d\\-\\/\\.]+)",
        "transform": "none"
    },
    {
        "name": "Clinician",
        "pattern": "(?:Clinician|Doctor|Physician|Dr\\.)\\s*:?\\s*([A-Za-z\\s\\.]+)",
        "transform": "none"
    }
]
```

### Application Settings

Configuration options in `config/app_config.json`:

- Window dimensions and interface settings
- Tesseract OCR configuration parameters
- Supported file format specifications
- Processing performance optimization settings

## Output Format

Excel output includes:

- **Data Sheet**: Extracted information with configurable column structure
- **Summary Sheet**: Processing statistics and success metrics
- **Formatted Headers**: Professional styling with optimized column widths
- **Data Validation**: Clear distinction between successful and failed extractions

## Troubleshooting

### Common Issues

1. **Dependency Errors**
   - Verify installation: `pip install -r requirements.txt`
   - Confirm Python version compatibility (3.8+)

2. **Tesseract OCR Issues**
   - Ensure Tesseract OCR installation
   - Verify system PATH configuration or set TESSDATA_PREFIX environment variable

3. **File Access Problems**
   - Confirm read permissions for data directories
   - Verify write permissions for output locations

4. **OCR Accuracy Issues**
   - Check source image quality and resolution
   - Adjust Tesseract configuration parameters
   - Consider image preprocessing for optimization

## Development

### Technical Requirements

- Python 3.8+
- PyQt6
- pytesseract (requires Tesseract OCR)
- PyMuPDF
- openpyxl
- pandas
- Pillow

## Healthcare Integration

The application provides enterprise-grade features for healthcare environments:

- **Intuitive Interface** for non-technical personnel
- **Configurable Processing Rules** without code modification requirements
- **Batch Processing Capabilities** for high-volume workflows
- **Comprehensive Audit Logging** for compliance requirements
- **Excel Compatibility** with existing healthcare information systems
- **Localization Support** for international deployments

## Technical Support

For technical assistance:
1. Review application activity logs
2. Analyze console output for error details
3. Verify file permissions and directory structure compliance
