#!/usr/bin/env python3
"""
Build script to create a portable .exe file for Looper
This script uses PyInstaller to package the application into a single executable
"""

import os
import sys
import subprocess
import shutil
import tempfile

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

def create_spec_file(build_dir):
    """Create a custom .spec file for better control over the build"""
    looper_py = os.path.join(build_dir, 'src', 'looper.py').replace('\\', '/')
    src_path = os.path.join(build_dir, 'src').replace('\\', '/')
    logo_png = os.path.join(build_dir, 'assets', 'logos', 'looper_logo.png').replace('\\', '/')
    icon_ico = os.path.join(build_dir, 'assets', 'icons', 'looper_icon.ico').replace('\\', '/')
    logo_small = os.path.join(build_dir, 'assets', 'logos', 'looper_logo_small.png').replace('\\', '/')
    logo_tiny = os.path.join(build_dir, 'assets', 'logos', 'looper_logo_tiny.png').replace('\\', '/')
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{looper_py}'],
    pathex=['{src_path}'],
    binaries=[],
    datas=[
        ('{logo_png}', '.'),
        ('{icon_ico}', '.'),
        ('{logo_small}', '.'),
        ('{logo_tiny}', '.')
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
    icon='{icon_ico}',  # Cool loop icon
    version_info=None
)
'''
    
    spec_file_path = os.path.join(build_dir, 'looper.spec')
    with open(spec_file_path, 'w') as f:
        f.write(spec_content)
    
    print("✓ Created custom .spec file")
    return spec_file_path

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
            exe_src = os.path.join(build_dir, 'dist', 'Looper_v0.9_by_Ghosteam.exe')
            exe_dst = os.path.join(original_cwd, 'dist', 'Looper_v0.9_by_Ghosteam.exe')
            os.makedirs(os.path.dirname(exe_dst), exist_ok=True)
            shutil.copy2(exe_src, exe_dst)
            print(f"✓ Executable copied to: {exe_dst}")
            return True
        else:
            print("✗ Build failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False
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
    
    # Keep the dist directory with the executable

def main():
    """Main build process"""
    print("=" * 50)
    print("LOOPER v0.9 - Executable Builder")
    print("by Ghosteam")
    print("=" * 50)
    
    # Check if looper.py exists in src directory
    if not os.path.exists('../src/looper.py'):
        print("✗ looper.py not found in src directory")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Create clean build environment
    build_dir = create_clean_build_environment()
    
    try:
        # Create spec file
        spec_file_path = create_spec_file(build_dir)
        
        # Build executable
        if not build_executable(build_dir, spec_file_path):
            return False
    finally:
        # Clean up temporary files
        cleanup_build_files(build_dir)
    
    # Check if executable was created
    exe_path = os.path.join('dist', 'Looper_v0.9_by_Ghosteam.exe')
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
        print(f"✓ Executable created: {exe_path}")
        print(f"✓ File size: {file_size:.1f} MB")
        
        # Cleanup already done in try/finally block
        
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
