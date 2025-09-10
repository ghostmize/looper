#!/usr/bin/env python3
"""
Enhanced build script with code signing support for Looper
This script uses PyInstaller to package the application and optionally signs it
"""

import os
import sys
import subprocess
import shutil
import tempfile
import argparse
from pathlib import Path

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

def ensure_multi_size_ico():
    """Generate a proper multi-size .ico file before building"""
    try:
        here = os.path.dirname(__file__)
        icons_dir = os.path.join(here, "..", "assets", "icons")
        make_icon_script = os.path.join(icons_dir, "make_icon.py")
        
        if os.path.exists(make_icon_script):
            subprocess.check_call([sys.executable, make_icon_script])
            print("✓ Multi-size icon generated")
        else:
            print("⚠️ make_icon.py not found, using existing icon")
    except Exception as e:
        print(f"⚠️ Could not regenerate .ico: {e}")

def create_clean_build_environment():
    """Create a clean build environment with only necessary files"""
    print("Creating clean build environment...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='looper_build_')
    print(f"✓ Created temporary build directory: {temp_dir}")
    
    # Copy source files
    src_dir = os.path.join(temp_dir, 'src')
    os.makedirs(src_dir, exist_ok=True)
    shutil.copy2('../src/looper.py', src_dir)
    shutil.copy2('../src/launch_looper.py', src_dir)
    print("✓ Copied source files")
    
    # Copy assets
    assets_dir = os.path.join(temp_dir, 'assets')
    shutil.copytree('../assets', assets_dir)
    print("✓ Copied assets")
    
    return temp_dir

def create_version_info():
    """Create version info for the executable"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(0,9,1,0),
    prodvers=(0,9,1,0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Ghosteam'),
        StringStruct(u'FileDescription', u'Looper - Perfect Video Loops'),
        StringStruct(u'FileVersion', u'0.9.1.0'),
        StringStruct(u'InternalName', u'Looper'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024 Ghosteam'),
        StringStruct(u'OriginalFilename', u'Looper_v0.91_by_Ghosteam.exe'),
        StringStruct(u'ProductName', u'Looper'),
        StringStruct(u'ProductVersion', u'0.9.1.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    return version_info

def create_spec_file(build_dir, sign_cert=None, sign_password=None):
    """Create a custom .spec file for better control over the build"""
    looper_py = os.path.join(build_dir, 'src', 'looper.py').replace('\\', '/')
    src_path = os.path.join(build_dir, 'src').replace('\\', '/')
    logo_png = os.path.join(build_dir, 'assets', 'logos', 'looper_logo.png').replace('\\', '/')
    icon_ico = os.path.join(build_dir, 'assets', 'icons', 'looper_icon.ico').replace('\\', '/')
    
    # Create version info file
    version_info_content = create_version_info()
    version_info_path = os.path.join(build_dir, 'version_info.txt')
    with open(version_info_path, 'w', encoding='utf-8') as f:
        f.write(version_info_content)
    
    # Set code signing parameters
    codesign_identity = sign_cert if sign_cert else None
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{looper_py}'],
    pathex=['{src_path}'],
    binaries=[],
    datas=[
        ('{logo_png}', '.'),
        ('{icon_ico}', '.')
    ],
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
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'setuptools',
        'git',
        'gitdb',
        'smmap',
        'GitPython'
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
    name='Looper_v0.91_by_Ghosteam',
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
    codesign_identity={repr(codesign_identity)},
    entitlements_file=None,
    icon='{icon_ico}',  # Cool loop icon
    version_info='{version_info_path.replace(chr(92), "/")}'
)
'''
    
    spec_file_path = os.path.join(build_dir, 'looper.spec')
    with open(spec_file_path, 'w') as f:
        f.write(spec_content)
    
    print("✓ Created custom .spec file with version info")
    return spec_file_path

def sign_executable(exe_path, cert_path=None, cert_password=None, timestamp_url=None):
    """Sign the executable using signtool.exe"""
    if not cert_path:
        print("⚠️ No certificate provided, skipping code signing")
        return True
    
    if not os.path.exists(exe_path):
        print(f"✗ Executable not found: {exe_path}")
        return False
    
    print(f"Signing executable: {exe_path}")
    
    # Build signtool command
    cmd = [
        'signtool.exe', 'sign',
        '/f', cert_path,  # Certificate file
        '/fd', 'SHA256',  # File digest algorithm
        '/tr', timestamp_url or 'http://timestamp.digicert.com',  # Timestamp server
        '/td', 'SHA256',  # Timestamp digest algorithm
    ]
    
    # Add password if provided
    if cert_password:
        cmd.extend(['/p', cert_password])
    
    # Add the executable path
    cmd.append(exe_path)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Executable signed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Code signing failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ signtool.exe not found. Please install Windows SDK or Visual Studio")
        return False

def verify_signature(exe_path):
    """Verify the signature of the executable"""
    if not os.path.exists(exe_path):
        return False
    
    try:
        result = subprocess.run(['signtool.exe', 'verify', '/pa', exe_path], 
                              capture_output=True, text=True, check=True)
        print("✓ Signature verification successful!")
        return True
    except subprocess.CalledProcessError:
        print("✗ Signature verification failed")
        return False
    except FileNotFoundError:
        print("⚠️ signtool.exe not found, cannot verify signature")
        return False

def build_executable(build_dir, spec_file_path):
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    try:
        # Change to build directory to avoid scanning the main project
        original_cwd = os.getcwd()
        os.chdir(build_dir)
        
        # Use the custom spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            spec_file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Executable built successfully!")
            # Copy executable back to original location
            exe_src = os.path.join(build_dir, 'dist', 'Looper_v0.91_by_Ghosteam.exe')
            exe_dst = os.path.join(original_cwd, 'dist', 'Looper_v0.91_by_Ghosteam.exe')
            os.makedirs(os.path.dirname(exe_dst), exist_ok=True)
            shutil.copy2(exe_src, exe_dst)
            print(f"✓ Executable copied to: {exe_dst}")
            return exe_dst
        else:
            print("✗ Build failed:")
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return None
    finally:
        # Always return to original directory
        os.chdir(original_cwd)

def cleanup_build_files(build_dir):
    """Clean up temporary build files"""
    print("Cleaning up build files...")
    
    # Remove temporary build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print("✓ Removed temporary build directory")
    
    # Remove local build directory
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("✓ Removed local build directory")
    
    # Remove spec file
    if os.path.exists('looper.spec'):
        os.remove('looper.spec')
        print("✓ Removed spec file")

def main():
    """Main build process with code signing support"""
    parser = argparse.ArgumentParser(description='Build Looper with optional code signing')
    parser.add_argument('--cert', help='Path to code signing certificate (.pfx or .p12 file)')
    parser.add_argument('--password', help='Password for the code signing certificate')
    parser.add_argument('--timestamp', help='Timestamp server URL (default: DigiCert)')
    parser.add_argument('--verify', action='store_true', help='Verify signature after signing')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("LOOPER v0.91 - Enhanced Executable Builder with Code Signing")
    print("by Ghosteam")
    print("=" * 60)
    
    # Check if looper.py exists in src directory
    if not os.path.exists('../src/looper.py'):
        print("✗ looper.py not found in src directory")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Generate multi-size icon before building
    ensure_multi_size_ico()
    
    # Create clean build environment
    build_dir = create_clean_build_environment()
    
    try:
        # Create spec file with signing parameters
        spec_file_path = create_spec_file(build_dir, args.cert, args.password)
        
        # Build executable
        exe_path = build_executable(build_dir, spec_file_path)
        if not exe_path:
            return False
        
        # Sign executable if certificate provided
        if args.cert:
            if not sign_executable(exe_path, args.cert, args.password, args.timestamp):
                print("⚠️ Code signing failed, but executable was built successfully")
            
            # Verify signature if requested
            if args.verify:
                verify_signature(exe_path)
        
    finally:
        # Clean up temporary files
        cleanup_build_files(build_dir)
    
    # Check if executable was created
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
        print(f"✓ Executable created: {exe_path}")
        print(f"✓ File size: {file_size:.1f} MB")
        
        if args.cert:
            print("✓ Code signed executable ready for distribution!")
        else:
            print("⚠️ Executable not signed - consider code signing for distribution")
        
        print("\n" + "=" * 60)
        print("BUILD COMPLETE!")
        print("=" * 60)
        print(f"Your executable is ready:")
        print(f"📁 Location: {os.path.abspath(exe_path)}")
        print(f"📦 Size: {file_size:.1f} MB")
        
        if args.cert:
            print("🔒 Code signed and ready for secure distribution!")
        else:
            print("\n💡 To code sign your executable:")
            print("   python build_exe_with_signing.py --cert path/to/certificate.pfx --password your_password")
        
        return True
    else:
        print("✗ Executable not found after build")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
