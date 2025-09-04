# Clinical Data Extractor - Executable Deployment Guide

## Overview

This guide explains how to create and deploy a standalone executable version of the Clinical Data Extractor for healthcare environments where Python may not be installed.

## Enhanced Error Handling

The application includes comprehensive dependency validation:

### Startup Validation
- **Immediate Tesseract Check**: Application validates Tesseract availability on startup
- **User-Friendly Warnings**: Clear dialog boxes explain missing dependencies
- **Graceful Degradation**: PDF extraction continues to work without Tesseract
- **Smart File Type Detection**: Warns users when attempting to process images without OCR

### Runtime Protection
- **Input Validation**: Checks file types against available capabilities
- **Clear Error Messages**: Specific feedback about processing errors
- **No Silent Failures**: All errors are logged and reported to users

## Creating Executables

### Method 1: Using PyInstaller (Recommended)

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Run the build script**:
   ```bash
   build_windows.bat
   ```

3. **Or use PyInstaller directly**:
   ```bash
   pyinstaller cde_app.spec --clean
   ```

### Method 2: Using auto-py-to-exe (GUI)

1. **Install the GUI tool**:
   ```bash
   pip install auto-py-to-exe
   ```

2. **Launch the GUI**:
   ```bash
   auto-py-to-exe
   ```

3. **Configure settings**:
   - Script Location: `main.py`
   - Onefile: Yes (creates single executable)
   - Console Window: No (GUI application)
   - Additional Files: Add `config` folder

## Deployment Strategies

### Strategy 1: Tesseract Bundled (Recommended for Healthcare)

**Advantages**: Complete standalone solution
**Disadvantages**: Larger file size (~200MB)

1. Install Tesseract with language packs
2. Copy Tesseract installation to `tesseract/` folder
3. Update application config to use bundled Tesseract
4. Create installer package with both executable and Tesseract

### Strategy 2: Tesseract Separate Installation

**Advantages**: Smaller executable (~50MB)
**Disadvantages**: Requires Tesseract installation on each machine

1. Create executable without Tesseract
2. Provide Tesseract installer alongside executable
3. Include installation instructions
4. Application will detect and warn if Tesseract is missing

### Strategy 3: Network Deployment

**Advantages**: Centralized updates, single installation
**Disadvantages**: Requires network access

1. Install on network share
2. Create shortcut on user desktops
3. Single Tesseract installation serves all users

## Healthcare Deployment Recommendations

### For IT Departments

1. **Test Environment Setup**:
   ```
   1. Create clean Windows VM
   2. Install only the executable (no Python/dependencies)
   3. Test with sample medical reports
   4. Verify Turkish language support
   5. Test Excel output compatibility
   ```

2. **Production Deployment**:
   ```
   Option A: MSI Installer Package
   - Include executable + Tesseract + sample data
   - Silent installation capability
   - Add to software deployment tools
   
   Option B: Portable Package
   - ZIP file with executable + dependencies
   - Extract and run anywhere
   - No admin rights required
   ```

3. **User Training Package**:
   ```
   Include:
   - User manual with screenshots
   - Sample data for practice
   - Troubleshooting guide
   - Contact information for IT support
   ```

### For End Users

1. **Installation**: Extract to desired folder (e.g., `C:\ClinicalDataExtractor\`)
2. **First Run**: Application will validate all dependencies
3. **If Tesseract Missing**: Follow installation instructions in the warning dialog
4. **Testing**: Select your own files/folders to test extraction functionality

## Troubleshooting Executable Issues

### Common Problems and Solutions

1. **"Application failed to start"**
   - Cause: Missing Visual C++ Redistributables
   - Solution: Install Microsoft Visual C++ Redistributable

2. **"DLL load failed"**
   - Cause: Architecture mismatch (32-bit vs 64-bit)
   - Solution: Rebuild executable for correct architecture

3. **"Tesseract not found" (in executable)**
   - Cause: Tesseract path hardcoded incorrectly
   - Solution: Use relative paths or bundle Tesseract

4. **Large executable size**
   - Cause: All dependencies included
   - Solution: Use `--exclude-module` for unused packages

5. **Slow startup**
   - Cause: Antivirus scanning large executable
   - Solution: Add executable to antivirus whitelist

## Deployment Checklist

### Before Creating Executable:
- [ ] Run `python validate_system.py` successfully
- [ ] Test application with sample data
- [ ] Verify all extraction rules work correctly
- [ ] Test Turkish character support
- [ ] Confirm Excel output format

### After Creating Executable:
- [ ] Test on clean Windows system (no Python)
- [ ] Verify Tesseract detection and warnings
- [ ] Test with actual medical reports
- [ ] Confirm file permissions work correctly
- [ ] Validate Excel export functionality

### For Hospital Distribution:
- [ ] Create user documentation
- [ ] Prepare IT installation guide
- [ ] Test on hospital network environment
- [ ] Verify compatibility with hospital Excel versions
- [ ] Prepare troubleshooting contacts

## Version Information

When building executables, consider adding version information:

1. **Create version_info.txt**:
   ```
   VSVersionInfo(
       ffi=FixedFileInfo(
           filevers=(1, 0, 0, 0),
           prodvers=(1, 0, 0, 0),
           mask=0x3f,
           flags=0x0,
           OS=0x4,
           fileType=0x1,
           subtype=0x0,
           date=(0, 0)
       ),
       kids=[
           StringFileInfo([
               StringTable('040904B0', [
                   StringStruct('CompanyName', 'Metanome'),
                   StringStruct('FileDescription', 'Clinical Data Extractor'),
                   StringStruct('FileVersion', '1.0.0.0'),
                   StringStruct('ProductName', 'Clinical Data Extractor'),
                   StringStruct('ProductVersion', '1.0.0.0')
               ])
           ]),
           VarFileInfo([VarStruct('Translation', [1033, 1200])])
       ]
   )
   ```

2. **Reference in spec file**: Update `cde_app.spec` to include version information

## Cross-Platform Considerations

### Windows (Primary Target)
- Use `.exe` extension
- Include Visual C++ dependencies
- Test on Windows 10/11
- Consider Windows Defender compatibility

### macOS (Optional)
- Create `.app` bundle
- Handle macOS security restrictions
- Test on different macOS versions

### Linux (Advanced)
- Create AppImage for portability
- Handle different distributions
- Consider dependency variations

## 📞 Support and Maintenance

### For Hospital IT Teams:
1. **Update Process**: How to deploy new versions
2. **Backup Strategy**: Preserve extraction rules and settings
3. **User Support**: Common issues and solutions
4. **Performance Monitoring**: Track extraction success rates

### For Developers:
1. **Build Automation**: CI/CD for executable creation
2. **Testing Matrix**: Multiple OS and dependency versions
3. **Error Reporting**: Collect logs from deployed executables
4. **Feature Requests**: Channel for hospital feedback

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Contact**: Metanome Development Team
