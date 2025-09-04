# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for Clinical Data Extractor.
This file defines how to build the executable.

Usage:
    pyinstaller cde_app.spec

For cross-platform considerations:
- Windows: Bundles all dependencies including DLLs
- Include Tesseract separately or ensure it's installed on target systems
- Config files and demo data are included in the bundle
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

# Application info
app_name = 'Clinical_Data_Extractor'
main_script = 'main.py'

# Collect all data files
datas = []

# Add config files
datas += [('config/*', 'config')]

# Add demo data (optional)
datas += [('demo/*', 'demo')]

# Add any additional resource files
if os.path.exists('resources'):
    datas += [('resources/*', 'resources')]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'pytesseract',
    'fitz',  # PyMuPDF
    'openpyxl',
    'pandas',
    'PIL',
    'regex',
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
    'matplotlib',  # Not used
    'numpy.random',  # Might not be needed
]

# Analysis
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable (optional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app_icon.ico' if os.path.exists('resources/app_icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None
)
