@echo off
REM Build script for Clinical Data Extractor (Windows)
REM This script creates a standalone executable for Windows distribution

echo ======================================
echo Clinical Data Extractor - Build Script
echo ======================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is available
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Running system validation...
python validate_system.py
if errorlevel 1 (
    echo.
    echo WARNING: System validation found issues.
    echo The executable may not work properly on target systems.
    echo.
    set /p continue="Do you want to continue anyway? (y/N): "
    if /i not "!continue!"=="y" (
        echo Build cancelled.
        pause
        exit /b 1
    )
)

echo.
echo Building executable...
echo This may take several minutes...

REM Create build directory
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM Build using spec file (recommended)
if exist "cde_app.spec" (
    echo Using spec file for build...
    pyinstaller cde_app.spec --clean
) else (
    echo Using direct PyInstaller command...
    pyinstaller main.py ^
        --name "Clinical_Data_Extractor" ^
        --windowed ^
        --onefile ^
        --add-data "config;config" ^
        --add-data "demo;demo" ^
        --hidden-import "PyQt6.QtCore" ^
        --hidden-import "PyQt6.QtGui" ^
        --hidden-import "PyQt6.QtWidgets" ^
        --hidden-import "pytesseract" ^
        --hidden-import "fitz" ^
        --hidden-import "openpyxl" ^
        --hidden-import "pandas" ^
        --clean
)

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)

echo.
echo ======================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ======================================
echo.
echo Executable location: dist\Clinical_Data_Extractor.exe
echo.
echo IMPORTANT NOTES:
echo 1. Tesseract OCR must be installed on target systems
echo 2. Or bundle Tesseract with your distribution package
echo 3. Test the executable on a clean system before distribution
echo.
echo Distribution checklist:
echo [ ] Test executable on clean Windows system
echo [ ] Verify Tesseract OCR installation instructions
echo [ ] Include sample data and documentation
echo [ ] Test with actual hospital data
echo.

REM Optionally copy additional files to dist folder
if exist "README.md" copy "README.md" "dist\"
if exist "INSTALL.md" copy "INSTALL.md" "dist\"
if exist "requirements.txt" copy "requirements.txt" "dist\"

echo Additional files copied to dist folder.
echo.
echo Build complete! Check dist\ folder for your executable.
pause
