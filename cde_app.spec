# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for Clinical Data Extractor.
This file defines how to build the executable.

Usage:
    pyinstaller cde_app.spec

For cross-platform considerations:
- Windows: Bundles all dependencies including DLLs
- Include Tesseract separately or ensure it's installed on target systems
- Config files are included in the bundle
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import sys

# Application info
app_name = 'Clinical_Data_Extractor'
main_script = 'main.py'

# Collect PyQt6 data files (for platform plugins, etc.)
qt_data = collect_data_files('PyQt6')

# Collect all data files
datas = []

# Add Qt platform data
datas += qt_data

# Add config files (required)
if os.path.exists('config'):
    datas += [('config', 'config')]

# Add any additional resource files (optional, only if directory exists)
if os.path.exists('resources'):
    datas += [('resources', 'resources')]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'pytesseract',
    'fitz',  # PyMuPDF
    'openpyxl',
    'pandas',
    'numpy',
    'PIL',
    'regex',
    # Qt platform plugins
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'PyQt6.QtPrintSupport',
    # Application modules
    'src.ui.main_window',
    'src.ui.settings_window',
    'src.core.text_extractor',
    'src.core.data_processor',
    'src.core.extraction_engine',
    'src.utils.config_manager',
    'src.utils.data_transformer',
    'src.utils.file_navigator'
]

# Binaries to exclude (optional, to reduce size)
excludes = [
    'tkinter',  # We're using PyQt6, not tkinter
    'matplotlib',  # Not used (if not needed)
]

# Analysis
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={
        'PyQt6': {
            'PyQt6.QtCore.QStandardPaths': ['plugins'],
        }
    },
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable - Using onedir for better performance
exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty - we're using onedir mode
    exclude_binaries=True,  # For onedir mode
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX for stability
    console=False,  # Disable console for clean deployment
    disable_windowed_traceback=False,
    icon='resources/app_icon.ico' if os.path.exists('resources/app_icon.ico') else None,
)

# Create directory distribution for better performance
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=app_name,
)
