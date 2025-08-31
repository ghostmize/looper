#!/usr/bin/env python3
"""
Looper Launcher - Perfect Video Loops
A lightweight launcher for the Looper application
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all required dependencies are available"""
    missing = []
    
    # Check Python version
    if sys.version_info < (3, 7):
        missing.append("Python 3.7 or higher")
    
    # Check required modules
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter")
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            missing.append("FFmpeg")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing.append("FFmpeg")
    
    return missing

def install_dependencies():
    """Install missing Python dependencies"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        return True
    except subprocess.CalledProcessError:
        return False

def show_error_dialog(missing_deps):
    """Show error dialog for missing dependencies"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    error_msg = "Missing dependencies:\n\n"
    for dep in missing_deps:
        error_msg += f"• {dep}\n"
    
    error_msg += "\nPlease install the missing dependencies and try again."
    
    messagebox.showerror("Dependencies Missing", error_msg)
    root.destroy()

def main():
    """Main launcher function"""
    print("Looper - Perfect Video Loops")
    print("=" * 30)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        print("Missing dependencies detected:")
        for dep in missing_deps:
            print(f"  - {dep}")
        
        # Try to install Python dependencies
        python_deps = [dep for dep in missing_deps if dep not in ["FFmpeg", "Python 3.7 or higher"]]
        if python_deps:
            print("\nAttempting to install Python dependencies...")
            if install_dependencies():
                print("Dependencies installed successfully!")
                # Re-check dependencies
                missing_deps = check_dependencies()
            else:
                print("Failed to install dependencies automatically.")
        
        if missing_deps:
            show_error_dialog(missing_deps)
            return 1
    
    # All dependencies available, launch the app
    print("All dependencies found. Launching Looper...")
    
    try:
        # Import and run the main application
        from looper import main as run_looper
        run_looper()
    except ImportError as e:
        print(f"Error importing looper module: {e}")
        return 1
    except Exception as e:
        print(f"Error running Looper: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

