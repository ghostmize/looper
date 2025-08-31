#!/usr/bin/env python3
"""
Build script to create a portable .exe file for Looper
This script uses PyInstaller to package the application into a single executable
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create a custom .spec file for better control over the build"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['looper.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'setuptools'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Looper_v0.9_by_Ghosteam',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='looper_icon.ico',  # Cool loop icon
    version_info=None
)
'''
    
    with open('looper.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Created custom .spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    try:
        # Use the custom spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "looper.spec"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Executable built successfully!")
            return True
        else:
            print("✗ Build failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def cleanup_build_files():
    """Clean up temporary build files"""
    print("Cleaning up build files...")
    
    # Remove build directory
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("✓ Removed build directory")
    
    # Remove spec file
    if os.path.exists('looper.spec'):
        os.remove('looper.spec')
        print("✓ Removed spec file")
    
    # Keep the dist directory with the executable

def main():
    """Main build process"""
    print("=" * 50)
    print("LOOPER v0.9 - Executable Builder")
    print("by Ghosteam")
    print("=" * 50)
    
    # Check if looper.py exists
    if not os.path.exists('looper.py'):
        print("✗ looper.py not found in current directory")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return False
    
    # Check if executable was created
    exe_path = os.path.join('dist', 'Looper_v0.9_by_Ghosteam.exe')
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
        print(f"✓ Executable created: {exe_path}")
        print(f"✓ File size: {file_size:.1f} MB")
        
        # Cleanup
        cleanup_build_files()
        
        print("\n" + "=" * 50)
        print("BUILD COMPLETE!")
        print("=" * 50)
        print(f"Your portable executable is ready:")
        print(f"📁 Location: {os.path.abspath(exe_path)}")
        print(f"📦 Size: {file_size:.1f} MB")
        print("\nYou can now distribute this single .exe file!")
        print("No installation required - just run the .exe")
        return True
    else:
        print("✗ Executable not found after build")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
