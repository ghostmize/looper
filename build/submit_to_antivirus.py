#!/usr/bin/env python3
"""
Script to help submit Looper executable to antivirus vendors for whitelisting
This is a free alternative to code signing for free tools
"""

import os
import sys
import webbrowser
import subprocess
from pathlib import Path

def check_executable_exists():
    """Check if the Looper executable exists"""
    exe_path = Path("dist/Looper_v0.91_by_Ghosteam.exe")
    if not exe_path.exists():
        print("❌ Executable not found!")
        print(f"Expected location: {exe_path.absolute()}")
        print("\nPlease build the executable first:")
        print("python build_exe.py")
        return None
    return exe_path

def get_file_info(exe_path):
    """Get file information for submission"""
    file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    return {
        'path': str(exe_path.absolute()),
        'size_mb': round(file_size, 1),
        'name': exe_path.name
    }

def submit_to_microsoft_defender():
    """Instructions for submitting to Microsoft Defender"""
    print("\n🛡️ Microsoft Defender (Windows Security)")
    print("=" * 50)
    print("1. Open Windows Security (Windows + I → Update & Security → Windows Security)")
    print("2. Go to Virus & threat protection")
    print("3. Click 'Manage settings' under Virus & threat protection settings")
    print("4. Scroll down to 'Exclusions' and click 'Add or remove exclusions'")
    print("5. Click 'Add an exclusion' → 'File'")
    print("6. Browse to your Looper executable")
    print("\nAlternative: Submit false positive report at:")
    print("https://www.microsoft.com/en-us/wdsi/filesubmission")

def submit_to_avast():
    """Open Avast submission page"""
    print("\n🛡️ Avast")
    print("=" * 50)
    print("Opening Avast sample submission page...")
    webbrowser.open("https://www.avast.com/submit-sample")
    print("Instructions:")
    print("1. Select 'False positive' as the reason")
    print("2. Upload your Looper executable")
    print("3. Add description: 'Looper - Video loop creation tool by Ghosteam'")

def submit_to_avg():
    """Open AVG submission page"""
    print("\n🛡️ AVG")
    print("=" * 50)
    print("Opening AVG sample submission page...")
    webbrowser.open("https://www.avg.com/submit-sample")
    print("Instructions:")
    print("1. Select 'False positive' as the reason")
    print("2. Upload your Looper executable")
    print("3. Add description: 'Looper - Video loop creation tool by Ghosteam'")

def submit_to_kaspersky():
    """Open Kaspersky submission page"""
    print("\n🛡️ Kaspersky")
    print("=" * 50)
    print("Opening Kaspersky OpenTip page...")
    webbrowser.open("https://opentip.kaspersky.com/")
    print("Instructions:")
    print("1. Upload your Looper executable")
    print("2. Select 'False positive' if it's flagged")
    print("3. Add description: 'Looper - Video loop creation tool by Ghosteam'")

def submit_to_malwarebytes():
    """Open Malwarebytes submission page"""
    print("\n🛡️ Malwarebytes")
    print("=" * 50)
    print("Opening Malwarebytes submission page...")
    webbrowser.open("https://www.malwarebytes.com/business/support")
    print("Instructions:")
    print("1. Look for 'Submit a sample' or 'False positive report'")
    print("2. Upload your Looper executable")
    print("3. Add description: 'Looper - Video loop creation tool by Ghosteam'")

def create_submission_package():
    """Create a package with submission information"""
    exe_path = check_executable_exists()
    if not exe_path:
        return
    
    file_info = get_file_info(exe_path)
    
    # Create submission info file
    info_content = f"""Looper v0.91 - Antivirus Whitelist Submission

File Information:
- Name: {file_info['name']}
- Size: {file_info['size_mb']} MB
- Path: {file_info['path']}

Software Information:
- Name: Looper
- Version: 0.91
- Developer: Ghosteam
- Description: A lightweight Windows application for creating perfect video loops with automatic crossfade transitions
- Website: [Your website/GitHub]
- License: Free

Purpose:
This is a legitimate video processing tool for VJs and video artists. It uses FFmpeg for video processing and OpenCV for image manipulation. The application is completely safe and does not contain any malicious code.

Technical Details:
- Built with PyInstaller
- Uses OpenCV, Pillow, and NumPy libraries
- Requires FFmpeg for video processing
- No network connectivity
- No system modifications
- No data collection

If this file is being flagged as a false positive, please whitelist it.
Thank you for your consideration.

Contact: [Your email]
"""
    
    info_file = Path("dist/antivirus_submission_info.txt")
    with open(info_file, 'w') as f:
        f.write(info_content)
    
    print(f"✅ Created submission info file: {info_file}")
    print(f"📁 Executable location: {file_info['path']}")

def main():
    """Main submission process"""
    print("🛡️ Looper - Antivirus Whitelist Submission Helper")
    print("=" * 60)
    print("This script helps you submit Looper to antivirus vendors")
    print("for whitelisting (free alternative to code signing)")
    print("=" * 60)
    
    # Check if executable exists
    exe_path = check_executable_exists()
    if not exe_path:
        return
    
    file_info = get_file_info(exe_path)
    print(f"✅ Found executable: {file_info['name']} ({file_info['size_mb']} MB)")
    
    # Create submission package
    create_submission_package()
    
    print("\n🎯 Recommended Submission Order:")
    print("1. Microsoft Defender (most important for Windows)")
    print("2. Avast (popular free antivirus)")
    print("3. AVG (popular free antivirus)")
    print("4. Kaspersky (if users report issues)")
    print("5. Malwarebytes (if users report issues)")
    
    while True:
        print("\n" + "=" * 60)
        print("Choose an option:")
        print("1. Microsoft Defender (Windows Security)")
        print("2. Avast")
        print("3. AVG")
        print("4. Kaspersky")
        print("5. Malwarebytes")
        print("6. Show all instructions")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            submit_to_microsoft_defender()
        elif choice == "2":
            submit_to_avast()
        elif choice == "3":
            submit_to_avg()
        elif choice == "4":
            submit_to_kaspersky()
        elif choice == "5":
            submit_to_malwarebytes()
        elif choice == "6":
            submit_to_microsoft_defender()
            submit_to_avast()
            submit_to_avg()
            submit_to_kaspersky()
            submit_to_malwarebytes()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please enter 1-7.")
    
    print("\n✅ Submission process complete!")
    print("\n💡 Tips:")
    print("- Submit to Microsoft Defender first (most important)")
    print("- It may take 1-2 weeks for whitelisting to take effect")
    print("- Encourage users to report false positives")
    print("- Consider GitHub Releases for better reputation")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")






