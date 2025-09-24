import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import threading
import json
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime
import tempfile
import shutil
import re
import shutil
from shutil import which

def resource_path(relpath: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller one-file builds"""
    if getattr(sys, '_MEIPASS', None):
        # PyInstaller one-file build - files are in the temp directory
        base = sys._MEIPASS
        return os.path.join(base, relpath)
    else:
        # Development mode - files are in the assets directory relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if relpath == 'looper_icon.ico':
            return os.path.join(project_root, 'assets', 'icons', 'looper_icon.ico')
        elif relpath == 'looper_logo.png':
            return os.path.join(project_root, 'assets', 'logos', 'looper_logo.png')
        else:
            return os.path.join(project_root, relpath)

# Optional: stable taskbar identity so Windows ties the window to your EXE icon
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Ghosteam.Looper.0.91')
except Exception:
    pass

class LooperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("◉ LOOPER v0.92 - Perfect Video Loops")
        self.root.geometry("950x950")
        
        # Optional: give the app a stable AppUserModelID so taskbar uses this icon
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Ghosteam.Looper')
        except Exception:
            pass
        
        # Unified color scheme - modern dark theme (cyan + magenta only)
        self.colors = {
            'bg_primary': '#0a0a0f',      # Main background
            'bg_secondary': '#1a1a2a',    # Secondary background
            'bg_container': '#2a2a3a',    # Container background
            'accent_primary': '#08c3d9',  # Primary accent (cyan)
            'accent_secondary': '#ff007a', # Secondary accent (magenta)
            'text_primary': '#ffffff',    # Primary text
            'text_secondary': '#cccccc',  # Secondary text
            'text_muted': '#666677',      # Muted text
            'success': '#08c3d9',         # Success (cyan)
            'warning': '#ff007a',         # Warning (magenta)
            'error': '#ff007a'            # Error (magenta)
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.resizable(True, True)
        self.root.minsize(800, 850)
        
        # Set window icon using resource_path for PyInstaller compatibility
        try:
            ico = resource_path('looper_icon.ico')
            print('Icon path:', ico, os.path.exists(ico))
            self.root.iconbitmap(ico)
        except Exception as e:
            print('⚠️ Could not load window icon:', e)
        
        # Video file info - now supports multiple files
        self.video_paths = []  # List of video file paths
        self.video_infos = []  # List of video info dictionaries
        self.output_paths = []  # List of output paths
        self.current_processing_index = 0
        
        # Processing state
        self.is_processing = False
        self.current_video_duration = 0  # For progress calculation
        
        # FFmpeg detection state
        self.ffmpeg_available = False
        self.ffmpeg_hap_ready = False  # whether ffmpeg has HAP encoder
        self.ffmpeg_exe = None   # absolute path to ffmpeg once found
        self.ff_has_hap = False  # whether ffmpeg supports HAP encoding
        self.ffmpeg_status_label = None
        self.ffmpeg_install_prompt_shown = False  # Prevent infinite prompts
        
        self.setup_ui()
        self.load_settings()
        
        # Check FFmpeg availability at startup
        self.root.after(100, self.check_ffmpeg_installation)
        
        # Check initial format after settings are loaded
        self.root.after(100, self.check_initial_format)
        
        # Bind resize event to update progress bar
        self.root.bind('<Configure>', self.on_window_resize)
        
    def setup_ui(self):
        # Configure styles
        self.setup_styles()
        
        # Main container with gradient-like effect
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header section - horizontal, classy, minimal
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Left side - Logo and title (horizontal layout)
        left_header = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        left_header.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Minimal title with icon
        title_container = tk.Frame(left_header, bg=self.colors['bg_primary'])
        title_container.pack(side=tk.LEFT)
        
        # Small FFmpeg status indicator on the left
        self.ffmpeg_status_label = tk.Label(
            left_header,
            text="🔍 Checking...",
            font=("Consolas", 8),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_primary']
        )
        self.ffmpeg_status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Simple loop icon (minimal)
        self.setup_logo(title_container)
        
        # Title and subtitle in horizontal layout
        text_container = tk.Frame(title_container, bg=self.colors['bg_primary'])
        text_container.pack(side=tk.LEFT, padx=(15, 0))
        
        title_label = tk.Label(
            text_container, 
            text="LOOPER", 
            font=("Consolas", 28, "bold"), 
            fg=self.colors['accent_primary'], 
            bg=self.colors['bg_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            text_container, 
            text=" • Perfect Video Loops", 
            font=("Consolas", 14), 
            fg=self.colors['text_secondary'], 
            bg=self.colors['bg_primary']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right side - Version and branding (horizontal)
        right_header = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        right_header.pack(side=tk.RIGHT)
        
        # Clickable Ghosteam label
        self.ghosteam_label = tk.Label(
            right_header, 
            text="Ghosteam", 
            font=("Consolas", 12, "bold"), 
            fg=self.colors['text_secondary'], 
            bg=self.colors['bg_primary'],
            cursor="hand2"
        )
        self.ghosteam_label.pack(side=tk.RIGHT)
        
        separator_label = tk.Label(
            right_header, 
            text=" | ", 
            font=("Consolas", 12), 
            fg=self.colors['text_muted'], 
            bg=self.colors['bg_primary']
        )
        separator_label.pack(side=tk.RIGHT)
        
        version_label = tk.Label(
            right_header, 
            text="v0.92", 
            font=("Consolas", 12, "bold"), 
            fg=self.colors['accent_secondary'], 
            bg=self.colors['bg_primary']
        )
        version_label.pack(side=tk.RIGHT)
        
        # Add hover effect to Ghosteam
        def on_ghosteam_enter(e):
            self.ghosteam_label.config(fg=self.colors['accent_secondary'])
        def on_ghosteam_leave(e):
            self.ghosteam_label.config(fg=self.colors['text_secondary'])
        
        self.ghosteam_label.bind("<Enter>", on_ghosteam_enter)
        self.ghosteam_label.bind("<Leave>", on_ghosteam_leave)
        self.ghosteam_label.bind("<Button-1>", self.show_about)
        
        # Elegant separator line
        separator_frame = tk.Frame(header_frame, bg=self.colors['accent_primary'], height=1)
        separator_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Setup file selection section
        self.setup_file_section(main_frame)
        
        # Setup settings section
        self.setup_settings_section(main_frame)
        
        # Setup action buttons
        self.setup_action_section(main_frame)
        
        # Setup progress section
        self.setup_progress_section(main_frame)
        
        # Recent files section removed for cleaner UI
    
    def setup_styles(self):
        """Setup custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
                # Configure futuristic combobox style
        style.configure('Futuristic.TCombobox',
                        fieldbackground=self.colors['bg_secondary'],
                        background=self.colors['accent_primary'],
                        foreground=self.colors['accent_primary'],
                        borderwidth=1,
                        relief='flat',
                        focuscolor=self.colors['accent_primary'])
        
                # Configure futuristic progressbar (keeping for compatibility)
        style.configure('Futuristic.Horizontal.TProgressbar',
                        background=self.colors['accent_primary'],
                        troughcolor=self.colors['bg_container'],
                        borderwidth=0,
                        lightcolor=self.colors['accent_primary'],
                        darkcolor=self.colors['accent_primary'])
    
    def setup_logo(self, parent):
        """Setup logo if available"""
        try:
            from PIL import Image, ImageTk
            
            # Use resource_path for PyInstaller compatibility
            logo_path = resource_path('looper_logo.png')
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Resize to 40x40 for the UI
                logo_img = logo_img.resize((40, 40), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = tk.Label(
                    parent,
                    image=self.logo_photo,
                    bg=self.colors['bg_primary']
                )
                logo_label.pack(side=tk.LEFT)
                print(f"✅ Loaded high-quality logo from: {logo_path}")
                return True
                    
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # If logo loading fails, create a simple geometric logo
        print("⚠️ Using fallback canvas logo")
        self.create_minimal_logo(parent)
        return False
    
    def create_simple_logo(self, parent):
        """Create a simple geometric logo using canvas"""
        canvas = tk.Canvas(parent, width=64, height=64, bg='#0a0a0f', highlightthickness=0)
        canvas.pack(side=tk.LEFT)
        
        # Draw a futuristic loop symbol
        center = 32
        radius = 20
        
        # Outer glow circles
        for i in range(3):
            r = radius + (i * 3)
            alpha_color = f"#{hex(50 - i*15)[2:].zfill(2)}ff{hex(170 - i*30)[2:].zfill(2)}"
            canvas.create_oval(center-r, center-r, center+r, center+r, 
                             outline=alpha_color, width=1)
        
        # Main loop
        canvas.create_oval(center-radius, center-radius, center+radius, center+radius, 
                         outline=self.colors['accent_primary'], width=3)
        
        # Inner infinity symbol
        canvas.create_oval(center-10, center-5, center, center+5, outline=self.colors['text_primary'], width=2)
        canvas.create_oval(center, center-5, center+10, center+5, outline=self.colors['text_primary'], width=2)
    
    def create_futuristic_button(self, parent, text, command, bg_color=None, fg_color=None, hover_color=None):
        """Create a futuristic-styled button with hover effects"""
        if bg_color is None:
            bg_color = self.colors['bg_container']
        if fg_color is None:
            fg_color = self.colors['accent_primary']
        if hover_color is None:
            hover_color = self.colors['accent_primary']
            
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Consolas", 11, "bold"),
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground=self.colors['bg_primary'],
            relief="flat",
            padx=25,
            pady=15,
            cursor="hand2",
            bd=0,
            highlightbackground=hover_color,
            highlightthickness=0
        )
        
        # Add hover effects
        def on_enter(e):
            button.config(bg=hover_color, fg=self.colors['bg_primary'])
        
        def on_leave(e):
            button.config(bg=bg_color, fg=fg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def create_minimal_logo(self, parent):
        """Create a minimal geometric logo with anti-aliasing simulation"""
        canvas = tk.Canvas(parent, width=40, height=40, bg=self.colors['bg_primary'], highlightthickness=0)
        canvas.pack(side=tk.LEFT)
        
        # Simple loop circle with modern styling
        center = 20
        radius = 15
        
        # Create multiple circles for anti-aliasing effect
        for i in range(3):
            r = radius - i
            alpha = 255 - (i * 50)
            color = f"#{hex(8)[2:].zfill(2)}{hex(195)[2:].zfill(2)}{hex(217)[2:].zfill(2)}"
            canvas.create_oval(center-r, center-r, center+r, center+r, 
                             outline=color, width=1)
        
        # Main loop circle
        canvas.create_oval(center-radius, center-radius, center+radius, center+radius, 
                         outline=self.colors['accent_primary'], width=2)
        
        # Inner accent with multiple layers
        for i in range(2):
            r = 8 - i
            color = f"#{hex(255)[2:].zfill(2)}{hex(0)[2:].zfill(2)}{hex(122)[2:].zfill(2)}"
            canvas.create_oval(center-r, center-r, center+r, center+r, 
                             outline=color, width=1)
    
    def show_about(self, event=None):
        """Show About dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Looper")
        about_window.geometry("400x250")
        about_window.configure(bg=self.colors['bg_primary'])
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Main container
        main_container = tk.Frame(about_window, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="LOOPER v0.92",
            font=("Consolas", 18, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # Description
        desc_label = tk.Label(
            main_container,
            text="This is a free tool made by",
            font=("Consolas", 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        desc_label.pack()
        
        # Clickable Ghosteam link
        ghosteam_link = tk.Label(
            main_container,
            text="Ghosteam",
            font=("Consolas", 12, "bold"),
            fg=self.colors['accent_secondary'],
            bg=self.colors['bg_primary'],
            cursor="hand2"
        )
        ghosteam_link.pack(pady=(5, 15))
        
        def open_website(e):
            import webbrowser
            webbrowser.open("https://www.ghosteaminc.com")
        
        def on_link_enter(e):
            ghosteam_link.config(fg=self.colors['accent_primary'])
        def on_link_leave(e):
            ghosteam_link.config(fg=self.colors['accent_secondary'])
        
        ghosteam_link.bind("<Button-1>", open_website)
        ghosteam_link.bind("<Enter>", on_link_enter)
        ghosteam_link.bind("<Leave>", on_link_leave)
        
        # Contact info
        contact_label = tk.Label(
            main_container,
            text="Contact via our shop for any requests",
            font=("Consolas", 10),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_primary']
        )
        contact_label.pack(pady=(0, 15))
        
        # Close button
        close_button = tk.Button(
            main_container,
            text="Close",
            command=about_window.destroy,
            font=("Consolas", 10, "bold"),
            bg=self.colors['bg_container'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent_primary'],
            activeforeground=self.colors['bg_primary'],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        close_button.pack()
        
        # Center the window on parent
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_width() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")
    
    
    def check_ffmpeg_installation(self):
        """Check if FFmpeg is installed and available with enhanced detection"""
        try:
            print("🔍 Checking FFmpeg installation...")
            
            # Method 1: Try to find FFmpeg in PATH
            ffmpeg_path = which('ffmpeg')
            if ffmpeg_path:
                print(f"Found FFmpeg in PATH: {ffmpeg_path}")
                if self.test_ffmpeg_execution():
                    return True
            
            # Method 2: Check common installation locations (Windows)
            if os.name == 'nt':
                common_paths = [
                    r"C:\ffmpeg\bin\ffmpeg.exe",
                    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                    r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                    os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*_*\ffmpeg-*\bin\ffmpeg.exe"),
                    r"C:\Users\%USERNAME%\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*_*\ffmpeg-*\bin\ffmpeg.exe"
                ]
                
                for path in common_paths:
                    if '*' in path:
                        # Handle wildcard paths
                        import glob
                        matches = glob.glob(path)
                        for match in matches:
                            if os.path.exists(match):
                                print(f"Found FFmpeg in common location: {match}")
                                if self.test_ffmpeg_execution(match):
                                    return True
                    else:
                        if os.path.exists(path):
                            print(f"Found FFmpeg in common location: {path}")
                            if self.test_ffmpeg_execution(path):
                                return True
            
            # Method 3: Try direct execution (in case PATH is not updated)
            if self.test_ffmpeg_execution():
                return True
            
            # FFmpeg not found or not working
            self.ffmpeg_available = False
            self.update_ffmpeg_status("FFmpeg Missing", self.colors['error'])
            print("❌ FFmpeg not found or not working")
            print("💡 Debug info:")
            print(f"   - PATH: {os.environ.get('PATH', 'Not set')}")
            print(f"   - which('ffmpeg'): {ffmpeg_path}")
            
            # Show installation prompt when FFmpeg is missing (only once)
            if not self.ffmpeg_install_prompt_shown:
                self.ffmpeg_install_prompt_shown = True
                self.root.after(1000, self.show_ffmpeg_installation_prompt)
            return False
            
        except Exception as e:
            print(f"Error checking FFmpeg: {e}")
            self.ffmpeg_available = False
            self.update_ffmpeg_status("FFmpeg Missing", self.colors['error'])
            
            # Show installation prompt when FFmpeg check fails (only once)
            if not self.ffmpeg_install_prompt_shown:
                self.ffmpeg_install_prompt_shown = True
                self.root.after(1000, self.show_ffmpeg_installation_prompt)
            return False
    
    def test_ffmpeg_execution(self, ffmpeg_path=None):
        '''Test if FFmpeg actually works and pin its absolute path.'''
        try:
            # Resolve the executable we are about to test
            exe = ffmpeg_path
            if not exe:
                from shutil import which
                exe = which('ffmpeg')
                # also try common install locations on Windows if PATH is stale
                if not exe and os.name == 'nt':
                    common = [
                        r'C:\ffmpeg\bin\ffmpeg.exe',
                        r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                        r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
                    ]
                    for cand in common:
                        if os.path.exists(cand):
                            exe = cand
                            break
            if not exe:
                print('❌ FFmpeg not found on PATH or common locations.')
                return False

            cmd = [exe, '-version']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                # Pin the absolute path to this exact binary
                self.ffmpeg_exe = os.path.abspath(exe)
                self.ffmpeg_available = True
                # Probe HAP support only once here
                self._ffmpeg_supports_hap()
                self.ffmpeg_hap_ready = self.ff_has_hap
                status = "FFmpeg ✓ HAP" if self.ff_has_hap else "FFmpeg (no HAP)"
                self.update_ffmpeg_status(status, self.colors['text_primary'] if self.ff_has_hap else self.colors['warning'])
                print('✅ FFmpeg is installed and working')
                if result.stdout:
                    version_line = result.stdout.split('\n')[0]
                    print(f'   Version: {version_line}')
                print(f'   Using: {self.ffmpeg_exe}')
                print(f'   HAP available: {self.ff_has_hap}')
                return True
            else:
                print(f'❌ FFmpeg execution failed with return code: {result.returncode}')
                if result.stderr:
                    print(f'   Error: {result.stderr[:200]}...')
                return False
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f'❌ FFmpeg execution error: {e}')
            return False
    
    def _ff(self, *args):
        """Build a subprocess arg list that always uses the resolved ffmpeg.exe."""
        exe = self.ffmpeg_exe or 'ffmpeg'
        return [exe, *args]

    def _ffmpeg_supports_hap(self):
        """Probe for HAP support in the current FFmpeg installation."""
        try:
            out = subprocess.run(
                self._ff('-hide_banner', '-encoders'),
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            enc = out.stdout.lower()
            # hap, hap_alpha, hap_q, hap_hq variants are all ok
            self.ff_has_hap = bool(re.search(r'^\s*v.*\bhap(_alpha|_q|_hq)?\b', enc, re.M))
        except Exception:
            self.ff_has_hap = False
        return self.ff_has_hap

    def ensure_hap_or_prompt(self) -> bool:
        """Return True only if ffmpeg exists AND has HAP. Otherwise, prompt to install full FFmpeg."""
        if not self.ffmpeg_available:
            self.show_ffmpeg_installation_prompt()
            return False
        if not self.ff_has_hap:
            messagebox.showerror(
                "HAP encoder required",
                "Your FFmpeg is installed but lacks the HAP encoder.\n\n"
                "Click OK to install the full build (Gyan.FFmpeg.Full) that includes HAP."
            )
            # Treat HAP-less FFmpeg as 'not installed' for HAP workflow
            self.ffmpeg_available = False
            self.show_ffmpeg_installation_prompt()
            return False
        return True

    def update_ffmpeg_status(self, text, color):
        """Update FFmpeg status label with minimalistic text"""
        if self.ffmpeg_status_label:
            # Make the text more minimalistic
            if "FFmpeg Installed" in text:
                display_text = "✓ FFmpeg"
            elif "FFmpeg Missing" in text:
                display_text = "✗ FFmpeg"
            elif "Installing" in text:
                display_text = "⏳ Installing..."
            elif "Installation Failed" in text:
                display_text = "✗ Install Failed"
            elif "Installation Timeout" in text:
                display_text = "⏰ Timeout"
            elif "Installation Error" in text:
                display_text = "✗ Error"
            elif "Checking" in text:
                display_text = "🔍 Checking..."
            else:
                display_text = text
            
            self.ffmpeg_status_label.config(text=display_text, fg=color)
    
    def install_ffmpeg_via_winget(self):
        """Install FFmpeg using winget"""
        try:
            print("🚀 Installing FFmpeg via winget...")
            self.update_ffmpeg_status("Installing FFmpeg...", self.colors['accent_primary'])
            
            # Run winget install command - use full build with all encoders
            cmd = [
                'winget', 'install', 'Gyan.FFmpeg.Full',
                '--accept-package-agreements',
                '--accept-source-agreements',
                '--silent'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                print("✅ FFmpeg installed successfully")
                
                # Try to resolve the installed FFmpeg path immediately
                possible = [
                    r"C:\ffmpeg\bin\ffmpeg.exe",
                    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                    r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*_*\ffmpeg-*\bin\ffmpeg.exe"),
                ]
                resolved = None
                import glob
                for p in possible:
                    if '*' in p:
                        matches = glob.glob(p)
                        if matches:
                            # pick latest by version folder name
                            matches.sort(reverse=True)
                            resolved = matches[0]
                            break
                    elif os.path.exists(p):
                        resolved = p
                        break

                if not resolved:
                    # final fallback to which (if PATH updated in this very session)
                    from shutil import which
                    resolved = which('ffmpeg')

                if resolved:
                    self.ffmpeg_exe = os.path.abspath(resolved)
                    self._ffmpeg_supports_hap()
                    self.ffmpeg_hap_ready = self.ff_has_hap
                    print(f'✅ FFmpeg path pinned to: {self.ffmpeg_exe}')
                    print(f'   HAP available: {self.ff_has_hap}')
                    
                    # Re-probe HAP and refuse to proceed if still missing
                    if not self.ff_has_hap:
                        messagebox.showerror("HAP still missing",
                            "Installed FFmpeg, but HAP encoder wasn't detected.\n"
                            "Please download the full static build from Gyan.dev (ffmpeg-git-full) and try again.")
                        return False
                
                self.update_ffmpeg_status("FFmpeg Installed", self.colors['text_primary'])
                self.ffmpeg_available = True
                
                # Show success message
                messagebox.showinfo(
                    "Installation Complete",
                    "FFmpeg has been installed successfully!\n\n"
                    "The application will now use the newly installed FFmpeg.\n"
                    "No restart required!"
                )
                return True
            else:
                print(f"❌ FFmpeg installation failed: {result.stderr}")
                self.update_ffmpeg_status("Installation Failed", self.colors['error'])
                messagebox.showerror(
                    "Installation Failed",
                    f"Failed to install FFmpeg:\n{result.stderr}\n\n"
                    "Please install FFmpeg manually from:\n"
                    "https://ffmpeg.org/download.html"
                )
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ FFmpeg installation timed out")
            self.update_ffmpeg_status("Installation Timeout", self.colors['error'])
            messagebox.showerror(
                "Installation Timeout",
                "FFmpeg installation timed out.\n\n"
                "Please try again or install manually from:\n"
                "https://ffmpeg.org/download.html"
            )
            return False
        except Exception as e:
            print(f"❌ Error installing FFmpeg: {e}")
            self.update_ffmpeg_status("Installation Error", self.colors['error'])
            messagebox.showerror(
                "Installation Error",
                f"Error installing FFmpeg: {str(e)}\n\n"
                "Please install FFmpeg manually from:\n"
                "https://ffmpeg.org/download.html"
            )
            return False
    
    def show_ffmpeg_installation_prompt(self):
        """Show prompt to install FFmpeg"""
        result = messagebox.askyesno(
            "FFmpeg Required",
            "FFmpeg is required to use LOOPER.\n\n"
            "Should it install now?\n\n"
            "This will use Windows Package Manager (winget) to install FFmpeg automatically."
        )
        
        if result:
            # Show installation progress
            self.update_ffmpeg_status("Installing FFmpeg...", self.colors['accent_primary'])
            
            # Run installation in a separate thread to avoid blocking UI
            def install_thread():
                success = self.install_ffmpeg_via_winget()
                if success:
                    # Don't re-check FFmpeg availability - user needs to restart
                    # The re-check would fail anyway since PATH isn't updated in current process
                    pass
            
            thread = threading.Thread(target=install_thread)
            thread.daemon = True
            thread.start()
        else:
            # Show manual installation instructions
            messagebox.showinfo(
                "Manual Installation",
                "To install FFmpeg manually:\n\n"
                "1. Download from: https://ffmpeg.org/download.html\n"
                "2. Extract to a folder (e.g., C:\\ffmpeg)\n"
                "3. Add the 'bin' folder to your system PATH\n"
                "4. Restart LOOPER\n\n"
                "Alternatively, you can use winget:\n"
                "winget install Gyan.FFmpeg.Full\n\n"
                "If you continue having issues after installation:\n"
                "• Try restarting your computer\n"
                "• Check if FFmpeg is in your system PATH\n"
                "• Contact support with the debug information"
            )
    
    def normalize_path(self, path):
        """Normalize path separators to use forward slashes consistently"""
        if path:
            return path.replace('\\', '/')
        return path
    
    def setup_file_section(self, main_frame):
        """Setup the file selection section"""
        # File selection section
        file_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        file_section.pack(fill=tk.X, pady=(0, 20))
        
        # Section header
        file_header = tk.Label(
            file_section,
            text="INPUT SOURCE",
            font=("Consolas", 14, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        file_header.pack(anchor='w', pady=(0, 12))
        
        # File selection container
        file_container = tk.Frame(file_section, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        file_container.pack(fill=tk.X, padx=2)
        
        # Inner container with padding
        file_inner = tk.Frame(file_container, bg=self.colors['bg_secondary'])
        file_inner.pack(fill=tk.X, padx=15, pady=15)
        
        # File selection buttons - fill horizontal space
        button_container = tk.Frame(file_inner, bg=self.colors['bg_secondary'])
        button_container.pack(fill=tk.X, pady=(0, 12))
        
        # Add drag and drop hint text above buttons
        drag_hint_label = tk.Label(
            file_inner,
            text="📁 Drag & drop video files anywhere in this area or use buttons below",
            font=("Consolas", 9),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_secondary']
        )
        drag_hint_label.pack(anchor='center', pady=(0, 8))
        
        # Create combined file selection button
        self.add_files_button = self.create_futuristic_button(
            button_container, "ADD FILES", self.select_files, 
            bg_color=self.colors['bg_container'], fg_color=self.colors['accent_primary'], hover_color=self.colors['accent_primary']
        )
        self.add_files_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.batch_folder_button = self.create_futuristic_button(
            button_container, "BATCH FOLDER", self.select_batch_folder,
            bg_color=self.colors['bg_container'], fg_color=self.colors['accent_primary'], hover_color=self.colors['accent_primary']
        )
        self.batch_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        # Setup drag and drop for the entire file section (not just buttons)
        self.setup_drag_drop(file_container)
        
        # File list display with elegant styling
        list_header = tk.Label(
            file_inner,
            text="▸ QUEUE FILES",
            font=("Consolas", 10, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_secondary']
        )
        list_header.pack(anchor='w', pady=(15, 8))
        
        # Files listbox with futuristic styling - reduced height
        listbox_container = tk.Frame(file_inner, bg=self.colors['bg_container'], relief='solid', bd=1, height=120)
        listbox_container.pack(fill=tk.X, pady=(0, 15))  # Changed from BOTH to X, added fixed height
        listbox_container.pack_propagate(False)  # Prevent height from expanding
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(listbox_container, bg=self.colors['bg_container'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)  # Remove container padding
        
        # Left side - Listbox
        listbox_left = tk.Frame(listbox_frame, bg=self.colors['bg_container'])
        listbox_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a scrollable frame for the files
        self.canvas = tk.Canvas(listbox_left, bg=self.colors['bg_container'], highlightthickness=0, bd=0, relief='flat')
        self.scrollbar = tk.Scrollbar(listbox_left, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_container'], bd=0, relief='flat')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # make the inner frame stretch to canvas width
        self.canvas_window = self.canvas.create_window((0, 0),
                                                       window=self.scrollable_frame,
                                                       anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        def _stretch_inner(event):
            # keep inner frame same width as the visible canvas
            self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
        
        self.canvas.bind("<Configure>", _stretch_inner)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # make wheel scroll work when hovering the queue
        def _focus_queue(_):
            self.canvas.focus_set()
            # On Windows/macOS, wheel events go to the focused widget
            self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

        def _unfocus_queue(_):
            self.canvas.unbind_all('<MouseWheel>')

        listbox_container.bind('<Enter>', _focus_queue)
        listbox_container.bind('<Leave>', _unfocus_queue)

        # Linux support (trackpad/wheel sends Button-4/5)
        listbox_container.bind('<Button-4>', lambda e: self.canvas.yview_scroll(-1, 'units'))
        listbox_container.bind('<Button-5>', lambda e: self.canvas.yview_scroll(1, 'units'))
        
        # Create a frame for each file row instead of a listbox
        self.files_container = tk.Frame(self.scrollable_frame, bg=self.colors['bg_container'], bd=0, relief='flat')
        self.files_container.pack(fill=tk.X, padx=0, pady=0)  # Changed from BOTH to X to prevent vertical expansion
        
        # We'll create individual file frames dynamically
        self.file_frames = []
        
        # No scrollbar needed for individual file frames
        
        # Remove buttons are now part of individual file frames
        
        # File summary with elegant styling
        self.file_summary_label = tk.Label(
            file_inner,
            text="◦ No files selected",
            font=("Consolas", 9),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_secondary']
        )
        self.file_summary_label.pack(anchor='w')
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for the file list"""
        # macOS sends small deltas; Windows is multiples of 120
        if sys.platform == 'darwin':
            step = -1 if event.delta > 0 else 1
        else:
            step = int(-event.delta / 120)
        self.canvas.yview_scroll(step, 'units')
    
    def setup_drag_drop(self, widget):
        """Setup drag and drop functionality for a widget"""
        # Store original colors and relief for restoration
        self.original_bg = widget.cget('bg')
        self.original_relief = widget.cget('relief')
        self.original_bd = widget.cget('bd')
        # Also store original highlight properties if present
        try:
            self.original_highlight_bg = widget.cget('highlightbackground')
            self.original_highlight_thickness = widget.cget('highlightthickness')
        except Exception:
            self.original_highlight_bg = ''
            self.original_highlight_thickness = 0
        self.drag_widget = widget
        
        def on_click(event):
            """Handle click to open file dialog"""
            try:
                files = filedialog.askopenfilenames(
                    title="Select Video Files",
                    filetypes=[
                        ("Video files", "*.mp4 *.mov *.avi *.mkv"),
                        ("MP4 files", "*.mp4"),
                        ("MOV files", "*.mov"),
                        ("All files", "*.*")
                    ]
                )
                if files:
                    self.handle_dropped_files(list(files))
            except Exception as e:
                print(f"Error handling file selection: {e}")
        
        # Bind click event to open file dialog
        widget.bind('<Button-1>', on_click)
        
        # Setup Windows drag and drop
        self.setup_windows_drag_drop(widget)
    
    def on_drag_enter(self, event):
        """Handle drag enter - show visual feedback with stroke highlight"""
        if hasattr(self, 'drag_widget') and self.drag_widget:
            self.drag_widget.config(
                bg='#1a2a3a',  # Darker background
                relief='solid',
                bd=4,  # Thicker border for stronger emphasis
                highlightbackground='#08c3d9',  # Cyan stroke
                highlightcolor='#08c3d9',
                highlightthickness=3  # Stroke thickness
            )
            # Update hint text
            for child in self.drag_widget.winfo_children():
                if isinstance(child, tk.Label) and "📁" in child.cget('text'):
                    child.config(text="📁 Drop files here!", fg='#08c3d9')
    
    def on_drag_leave(self, event):
        """Handle drag leave - restore original appearance"""
        if hasattr(self, 'drag_widget') and self.drag_widget:
            self.drag_widget.config(
                bg=self.original_bg,
                relief=self.original_relief,
                bd=self.original_bd,
                highlightbackground=self.original_highlight_bg if hasattr(self, 'original_highlight_bg') else '',
                highlightcolor=self.original_highlight_bg if hasattr(self, 'original_highlight_bg') else '',
                highlightthickness=self.original_highlight_thickness if hasattr(self, 'original_highlight_thickness') else 0
            )
            # Restore hint text
            for child in self.drag_widget.winfo_children():
                if isinstance(child, tk.Label) and "📁" in child.cget('text'):
                    child.config(text="📁 Drag & drop video files anywhere in this area or use buttons below", fg='#666677')
    
    def setup_windows_drag_drop(self, widget):
        """Setup Windows-specific drag and drop"""
        try:
            # Try to use tkinterdnd2 if available
            import tkinterdnd2 as tkdnd
            
            # Make the widget a drop target
            widget.drop_target_register(tkdnd.DND_FILES)
            
            # Bind drag-over events for visual feedback
            widget.dnd_bind('<<DropEnter>>', self.on_drag_enter)
            widget.dnd_bind('<<DropLeave>>', self.on_drag_leave)
            widget.dnd_bind('<<Drop>>', self.on_drop_files)
            
            print("✓ tkinterdnd2 drag and drop enabled with drag-over feedback")
            
        except ImportError:
            print("tkinterdnd2 not available - using click-to-select mode")
            # Update hint text to reflect click-only mode
            for child in widget.winfo_children():
                if isinstance(child, tk.Label) and "📁" in child.cget('text'):
                    child.config(text="📁 Click here to select video files", fg='#666677')
                    break
        except Exception as e:
            print(f"Error setting up tkinterdnd2 drag and drop: {e}")
            # Fallback to click-only mode
            for child in widget.winfo_children():
                if isinstance(child, tk.Label) and "📁" in child.cget('text'):
                    child.config(text="📁 Click here to select video files", fg='#666677')
                    break
    
    def on_drop_files(self, event):
        """Handle dropped files from tkinterdnd2"""
        try:
            print(f"Drop event received: {event}")
            print(f"Event data: {event.data}")
            
            if hasattr(event, 'data') and event.data:
                # Parse dropped file data
                files = self.parse_dropped_files(event.data)
                print(f"Parsed files: {files}")
                if files:
                    self.handle_dropped_files(files)
                else:
                    print("No valid video files found in dropped data")
            else:
                print("No data in drop event")
        except Exception as e:
            print(f"Error handling dropped files: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Ensure highlight clears shortly after drop completes
            if hasattr(self, 'root'):
                self.root.after(10, lambda: self.on_drag_leave(event))
    
    def parse_dropped_files(self, data):
        """Parse dropped file data"""
        files = []
        
        try:
            print(f"Parsing data: {data}")
            print(f"Data type: {type(data)}")
            
            if isinstance(data, str):
                # Handle tkinterdnd2 format - remove curly braces and split properly
                # The data comes as: {path1} {path2} etc.
                # We need to extract each path between curly braces
                import re
                
                # Find all content between curly braces
                pattern = r'\{([^}]+)\}'
                matches = re.findall(pattern, data)
                
                if matches:
                    # Use the regex matches
                    files = [path.strip() for path in matches if path.strip()]
                    print(f"Extracted file paths (regex): {files}")
                else:
                    # Fallback to other methods
                    if '\n' in data:
                        # Split by newlines
                        file_paths = data.split('\n')
                    elif '\r\n' in data:
                        # Split by Windows line endings
                        file_paths = data.split('\r\n')
                    else:
                        # Split by spaces and handle quoted paths
                        import shlex
                        file_paths = shlex.split(data)
                    
                    files = [path.strip() for path in file_paths if path.strip()]
                    print(f"Extracted file paths (fallback): {files}")
            
            # Filter for video files
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.MP4', '.MOV', '.AVI', '.MKV']
            video_files = []
            
            for file_path in files:
                print(f"Checking file: {file_path}")
                if any(file_path.lower().endswith(ext.lower()) for ext in video_extensions):
                    video_files.append(file_path)
                    print(f"Added video file: {file_path}")
                else:
                    print(f"Skipped non-video file: {file_path}")
            
            print(f"Final video files: {video_files}")
            return video_files
            
        except Exception as e:
            print(f"Error parsing dropped files: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_dropped_files_from_event(self, event):
        """Extract file paths from drop event"""
        try:
            # Try to get files from the event data
            if hasattr(event, 'data'):
                return self.parse_dropped_files(event.data)
            
            # Try to get from clipboard
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                try:
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                    files = data.split('\0')[:-1]  # Remove empty string at end
                    win32clipboard.CloseClipboard()
                    return files
                except:
                    win32clipboard.CloseClipboard()
            except ImportError:
                pass
                
        except Exception as e:
            print(f"Error extracting dropped files: {e}")
        
        return []
    
    def handle_dropped_files(self, file_paths):
        """Handle files dropped via drag and drop"""
        if not file_paths:
            return
        
        # Filter for video files
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.MP4', '.MOV', '.AVI', '.MKV']
        video_files = []
        
        for file_path in file_paths:
            if any(file_path.lower().endswith(ext.lower()) for ext in video_extensions):
                video_files.append(file_path)
        
        if video_files:
            # Add to existing list instead of replacing
            self.video_paths.extend(video_files)
            self.analyze_all_videos()
            self.update_file_display()
            self.process_button.config(state=tk.NORMAL)
            
            # Silent success - no popup messages
            print(f"✓ Added {len(video_files)} video file(s) to queue")
        else:
            print("⚠️ No valid video files found in dropped items")
    
    def setup_settings_section(self, main_frame):
        """Setup the settings section with horizontal layout"""
        # Settings section
        settings_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        settings_section.pack(fill=tk.X, pady=(0, 20))
        
        # Section header
        settings_header = tk.Label(
            settings_section,
            text="LOOP PARAMETERS",
            font=("Consolas", 14, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        settings_header.pack(anchor='w', pady=(0, 12))
        
        # Settings container
        settings_container = tk.Frame(settings_section, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        settings_container.pack(fill=tk.X, padx=2)
        
        # Inner container with horizontal layout for both settings
        settings_inner = tk.Frame(settings_container, bg=self.colors['bg_secondary'])
        settings_inner.pack(fill=tk.X, padx=15, pady=15)
        
        # Horizontal container for both settings
        horizontal_settings = tk.Frame(settings_inner, bg=self.colors['bg_container'], relief='solid', bd=1)
        horizontal_settings.pack(fill=tk.X)
        
        settings_row = tk.Frame(horizontal_settings, bg=self.colors['bg_container'])
        settings_row.pack(fill=tk.X, padx=20, pady=15)
        
        # Left side - Crossfade Duration
        left_settings = tk.Frame(settings_row, bg=self.colors['bg_container'])
        left_settings.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            left_settings,
            text="CROSSFADE DURATION",
            font=("Consolas", 11, "bold"),
            fg=self.colors['accent_secondary'],
            bg=self.colors['bg_container']
        ).pack(side=tk.LEFT)
        
        self.overlap_var = tk.DoubleVar(value=1.0)
        self.overlap_mode = tk.StringVar(value="seconds")  # "seconds" or "frames"
        
        spinbox_container = tk.Frame(left_settings, bg=self.colors['bg_container'])
        spinbox_container.pack(side=tk.RIGHT)
        
        self.overlap_spinbox = tk.Spinbox(
            spinbox_container,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.overlap_var,
            font=("Consolas", 11, "bold"),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent_primary'],
            insertbackground=self.colors['accent_primary'],
            relief="flat",
            width=6,
            bd=1,
            buttonbackground=self.colors['accent_primary'],
            selectbackground=self.colors['accent_primary'],
            selectforeground=self.colors['bg_primary']
        )
        self.overlap_spinbox.pack(side=tk.LEFT)
        
        # Toggle button for seconds/frames
        self.overlap_toggle = tk.Button(
            spinbox_container,
            text="SEC",
            command=self.toggle_overlap_mode,
            font=("Consolas", 9, "bold"),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['accent_secondary'],
            activeforeground=self.colors['bg_primary'],
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2"
        )
        self.overlap_toggle.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separator
        separator = tk.Frame(settings_row, bg=self.colors['accent_primary'], width=1)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=25)
        
        # Right side - Output Format
        right_settings = tk.Frame(settings_row, bg=self.colors['bg_container'])
        right_settings.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            right_settings,
            text="OUTPUT FORMAT",
            font=("Consolas", 11, "bold"),
            fg=self.colors['accent_secondary'],
            bg=self.colors['bg_container']
        ).pack(side=tk.LEFT)
        
        self.format_var = tk.StringVar(value="HAP")
        self.quality_var = tk.IntVar(value=18)  # Default CRF value for MP4
        
        combo_container = tk.Frame(right_settings, bg=self.colors['bg_container'])
        combo_container.pack(side=tk.RIGHT)
        
        format_combo = ttk.Combobox(
            combo_container,
            textvariable=self.format_var,
            values=["HAP", "MP4"],
            font=("Consolas", 11, "bold"),
            state="readonly",
            width=6,
            style='Futuristic.TCombobox'
        )
        format_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # Settings button for MP4 quality (initially hidden)
        self.settings_button = tk.Button(
            combo_container,
            text="⚙️",
            command=self.show_quality_slider,
            font=("Consolas", 10, "bold"),
            bg=self.colors['accent_secondary'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['accent_primary'],
            activeforeground=self.colors['bg_primary'],
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2"
        )
        
        # Bind format change to show/hide settings button
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # Format check will be done after settings are loaded
    
    def setup_action_section(self, main_frame):
        """Setup the action buttons section"""
        # Action section with futuristic design
        action_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        action_section.pack(pady=(0, 15))
        
        # Main process button - vibrant and modern
        self.process_button = tk.Button(
            action_section,
            text="⚡ GENERATE PERFECT LOOPS ⚡",
            command=self.process_videos,
            font=("Consolas", 18, "bold"),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['accent_secondary'],
            activeforeground=self.colors['bg_primary'],
            disabledforeground=self.colors['bg_primary'],
            relief="flat",
            bd=0,
            padx=60,
            pady=25,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.process_button.pack(pady=20)
        
        # Enhanced hover effect with color transitions
        def on_button_enter(e):
            if self.process_button['state'] != 'disabled':
                self.process_button.config(
                    bg=self.colors['accent_secondary'],
                    fg=self.colors['bg_primary'],
                    relief="raised",
                    bd=3
                )
                # Add a subtle glow effect
                self.process_button.config(highlightthickness=2, highlightbackground=self.colors['accent_secondary'])
        
        def on_button_leave(e):
            if self.process_button['state'] != 'disabled':
                self.process_button.config(
                    bg=self.colors['accent_primary'],
                    fg=self.colors['bg_primary'],
                    relief="flat",
                    bd=0
                )
                # Remove glow effect
                self.process_button.config(highlightthickness=0)
        
        self.process_button.bind("<Enter>", on_button_enter)
        self.process_button.bind("<Leave>", on_button_leave)
    
    def on_format_change(self, event=None):
        """Handle format selection change"""
        if self.format_var.get() == "MP4":
            self.settings_button.pack(side=tk.LEFT)
            return
        # HAP chosen → enforce
        self.settings_button.pack_forget()
        if not self.ensure_hap_or_prompt():
            # user will install; keep selection on HAP so behavior is clear
            pass
    
    def check_initial_format(self):
        """Check initial format and show settings button if needed"""
        if self.format_var.get() == "MP4":
            self.settings_button.pack(side=tk.LEFT)
        else:  # HAP default
            self.settings_button.pack_forget()
            self.ensure_hap_or_prompt()
    
    def toggle_overlap_mode(self):
        """Toggle between seconds and frames mode"""
        if self.overlap_mode.get() == "seconds":
            # Switch to frames mode
            self.overlap_mode.set("frames")
            self.overlap_toggle.config(text="FRAMES")
            # Convert current value to frames (assuming 30fps for conversion)
            current_seconds = self.overlap_var.get()
            frames = int(current_seconds * 30)
            self.overlap_var.set(frames)
            # Update spinbox range and increment
            self.overlap_spinbox.config(from_=1, to=300, increment=1)
        else:
            # Switch to seconds mode
            self.overlap_mode.set("seconds")
            self.overlap_toggle.config(text="SEC")
            # Convert current value to seconds
            current_frames = self.overlap_var.get()
            seconds = current_frames / 30
            self.overlap_var.set(round(seconds, 1))
            # Update spinbox range and increment
            self.overlap_spinbox.config(from_=0.1, to=10.0, increment=0.1)
    
    def show_quality_slider(self):
        """Show quality slider popup for MP4 encoding"""
        quality_window = tk.Toplevel(self.root)
        quality_window.title("MP4 Quality")
        quality_window.geometry("350x200")
        quality_window.configure(bg=self.colors['bg_primary'])
        quality_window.resizable(False, False)
        quality_window.transient(self.root)
        quality_window.grab_set()
        
        # Center the window
        quality_window.update_idletasks()
        x = (quality_window.winfo_screenwidth() // 2) - (quality_window.winfo_width() // 2)
        y = (quality_window.winfo_screenheight() // 2) - (quality_window.winfo_height() // 2)
        quality_window.geometry(f"+{x}+{y}")
        
        # Main container
        main_container = tk.Frame(quality_window, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="MP4 Quality",
            font=("Consolas", 14, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # Quality slider container
        slider_container = tk.Frame(main_container, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        slider_container.pack(fill=tk.X, pady=(0, 15))
        
        slider_inner = tk.Frame(slider_container, bg=self.colors['bg_secondary'])
        slider_inner.pack(fill=tk.X, padx=15, pady=12)
        
        # Quality label and value
        tk.Label(
            slider_inner,
            text="CRF:",
            font=("Consolas", 11, "bold"),
            fg=self.colors['accent_secondary'],
            bg=self.colors['bg_secondary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            slider_inner,
            textvariable=self.quality_var,
            font=("Consolas", 11, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_secondary'],
            width=3
        ).pack(side=tk.RIGHT)
        
        # Quality slider
        quality_slider = tk.Scale(
            main_container,
            from_=0,
            to=51,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            font=("Consolas", 9),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            highlightthickness=0,
            troughcolor=self.colors['bg_container'],
            activebackground=self.colors['accent_primary'],
            sliderrelief="flat",
            sliderlength=15,
            length=250
        )
        quality_slider.pack(pady=(0, 10))
        
        # Simple indicators
        indicators_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        indicators_frame.pack(fill=tk.X)
        
        tk.Label(
            indicators_frame,
            text="High Quality",
            font=("Consolas", 8),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_primary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            indicators_frame,
            text="Small File",
            font=("Consolas", 8),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_primary']
        ).pack(side=tk.RIGHT)
        
        # Close button
        close_button = tk.Button(
            main_container,
            text="Apply",
            command=quality_window.destroy,
            font=("Consolas", 10, "bold"),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['accent_secondary'],
            activeforeground=self.colors['bg_primary'],
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        close_button.pack(pady=(15, 0))
    
    def setup_progress_section(self, main_frame):
        """Setup the progress section"""
        # Progress section with futuristic design
        progress_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        progress_section.pack(fill=tk.X, pady=(0, 35))
        
        # Section header
        progress_header = tk.Label(
            progress_section,
            text="◦ PROCESSING STATUS",
            font=("Consolas", 14, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_primary']
        )
        progress_header.pack(anchor='w', pady=(0, 15))
        
        # Progress container
        progress_container = tk.Frame(progress_section, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        progress_container.pack(fill=tk.X, padx=5)
        
        # Inner container
        progress_inner = tk.Frame(progress_container, bg=self.colors['bg_secondary'])
        progress_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Progress bar with ultra-modern styling
        self.progress_var = tk.DoubleVar()
        progress_container = tk.Frame(progress_inner, bg=self.colors['bg_container'], padx=2, pady=2)
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        # Custom progress bar frame with border
        self.progress_bar_frame = tk.Frame(progress_container, bg=self.colors['bg_primary'], height=24, relief='solid', bd=1)
        self.progress_bar_frame.pack(fill=tk.X, padx=1, pady=1)
        self.progress_bar_frame.pack_propagate(False)
        
        # Progress bar fill (will be updated dynamically)
        self.progress_bar_fill = tk.Frame(self.progress_bar_frame, bg=self.colors['accent_primary'], width=0)
        self.progress_bar_fill.pack(side=tk.LEFT, fill=tk.Y, padx=1, pady=1)
        
        # Progress percentage label
        self.progress_label = tk.Label(
            progress_container,
            text="0%",
            font=("Consolas", 10, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_container']
        )
        self.progress_label.pack(anchor='e', pady=(5, 0))
        
        # Status label with terminal styling
        self.status_label = tk.Label(
            progress_inner,
            text="◦ SYSTEM READY - AWAITING INPUT ◦",
            font=("Consolas", 11),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        self.status_label.pack(pady=(5, 0))
    
    def setup_recent_files_section(self, main_frame):
        """Setup the recent files section"""
        # Recent files section with futuristic design
        recent_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        recent_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Section header
        recent_header = tk.Label(
            recent_section,
            text="◦ RECENT FILES",
            font=("Consolas", 14, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_primary']
        )
        recent_header.pack(anchor='w', pady=(0, 15))
        
        # Recent files container
        recent_container = tk.Frame(recent_section, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        recent_container.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Inner container
        recent_inner = tk.Frame(recent_container, bg=self.colors['bg_secondary'])
        recent_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Instructions
        recent_instruction = tk.Label(
            recent_inner,
            text="▸ DOUBLE-CLICK TO RELOAD",
            font=("Consolas", 9),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_secondary']
        )
        recent_instruction.pack(anchor='w', pady=(0, 8))
        
        # Recent files listbox
        self.recent_listbox = tk.Listbox(
            recent_inner,
            font=("Consolas", 10),
            bg=self.colors['bg_container'],
            fg=self.colors['accent_primary'],
            selectbackground=self.colors['accent_primary'],
            selectforeground=self.colors['bg_primary'],
            relief="flat",
            activestyle='none',
            highlightthickness=0
        )
        self.recent_listbox.pack(fill=tk.BOTH, expand=True)
        self.recent_listbox.bind('<Double-Button-1>', self.load_recent_file)
        
    def select_files(self):
        """Select one or multiple video files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv"),
                ("MP4 files", "*.mp4"),
                ("MOV files", "*.mov"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            # Add to existing list instead of replacing
            self.video_paths.extend(list(file_paths))
            self.analyze_all_videos()
            self.update_file_display()
            self.process_button.config(state=tk.NORMAL)
    
    def select_single_file(self):
        """Select a single video file"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv"),
                ("MP4 files", "*.mp4"),
                ("MOV files", "*.mov"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Add to existing list instead of replacing
            self.video_paths.append(file_path)
            self.analyze_all_videos()
            self.update_file_display()
            self.process_button.config(state=tk.NORMAL)
    
    def select_multiple_files(self):
        """Select multiple video files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Multiple Video Files",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv"),
                ("MP4 files", "*.mp4"),
                ("MOV files", "*.mov"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            # Add to existing list instead of replacing
            self.video_paths.extend(list(file_paths))
            self.analyze_all_videos()
            self.update_file_display()
            self.process_button.config(state=tk.NORMAL)
            # Recent files functionality removed
    
    def select_batch_folder(self):
        """Select a folder and process all video files in it"""
        folder_path = filedialog.askdirectory(
            title="Select Folder for Batch Processing"
        )
        
        if folder_path:
            # Find all video files in the folder
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.MP4', '.MOV', '.AVI', '.MKV']
            video_files = []
            
            for file in os.listdir(folder_path):
                if any(file.endswith(ext) for ext in video_extensions):
                    video_files.append(os.path.join(folder_path, file))
            
            if video_files:
                # Add to existing list instead of replacing
                self.video_paths.extend(sorted(video_files))  # Sort for consistent order
                self.analyze_all_videos()
                self.update_file_display()
                self.process_button.config(state=tk.NORMAL)
                # Recent files functionality removed
            else:
                messagebox.showinfo("No Videos Found", f"No video files found in:\n{folder_path}")
    
    def analyze_all_videos(self):
        """Analyze all selected video files"""
        self.video_infos = []
        
        for video_path in self.video_paths:
            try:
                cap = cv2.VideoCapture(video_path)
                
                if not cap.isOpened():
                    # Skip files that can't be opened
                    continue
                
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                # Get file size
                file_size = os.path.getsize(video_path)
                file_size_mb = file_size / (1024 * 1024)
                
                video_info = {
                    'path': video_path,
                    'fps': fps,
                    'frame_count': frame_count,
                    'width': width,
                    'height': height,
                    'duration': duration,
                    'file_size_mb': file_size_mb,
                    'filename': os.path.basename(video_path)
                }
                
                self.video_infos.append(video_info)
                cap.release()
                
            except Exception as e:
                print(f"Error analyzing {video_path}: {str(e)}")
                continue
    
    def update_file_display(self):
        """Update the file list display"""
        # Clear existing file frames
        for frame in self.file_frames:
            frame.destroy()
        self.file_frames.clear()
        
        if not self.video_infos:
            self.file_summary_label.config(text="No files in queue")
            return
        
        # Add files as individual rows
        total_size = 0
        total_duration = 0
        
        for i, video_info in enumerate(self.video_infos):
            # Create a frame for this file row
            file_frame = tk.Frame(self.files_container, bg=self.colors['bg_container'])
            file_frame.pack(fill=tk.X, pady=1)
            
            # File info with better alignment
            filename = video_info['filename']  # Show full filename
            resolution = f"{video_info['width']}x{video_info['height']}"
            duration = f"{video_info['duration']:.1f}s"
            fps = f"{video_info['fps']:.1f}fps"
            
            # Filename (left)
            filename_label = tk.Label(
                file_frame,
                text=filename,
                font=("Consolas", 9, "bold"),
                bg=self.colors['bg_container'],
                fg=self.colors['accent_primary'],
                anchor='w'
            )
            filename_label.grid(row=0, column=0, sticky="w", padx=(5, 0))
            
            # Resolution
            res_label = tk.Label(
                file_frame, 
                text=resolution, 
                font=("Consolas", 9),
                bg=self.colors['bg_container'], 
                fg=self.colors['text_primary']
            )
            res_label.grid(row=0, column=1, sticky="e", padx=(10, 5))
            
            # Duration
            dur_label = tk.Label(
                file_frame, 
                text=duration, 
                font=("Consolas", 9),
                bg=self.colors['bg_container'], 
                fg=self.colors['text_primary']
            )
            dur_label.grid(row=0, column=2, sticky="e", padx=(10, 5))
            
            # FPS
            fps_label = tk.Label(
                file_frame, 
                text=fps, 
                font=("Consolas", 9),
                bg=self.colors['bg_container'], 
                fg=self.colors['text_primary']
            )
            fps_label.grid(row=0, column=3, sticky="e", padx=(10, 5))
            
            # Remove button (far right)
            remove_btn = tk.Button(
                file_frame, 
                text="✕",
                command=lambda idx=i: self.remove_file_by_index(idx),
                font=("Consolas", 8, "bold"),
                bg=self.colors['accent_secondary'], 
                fg=self.colors['bg_primary'],
                activebackground=self.colors['accent_primary'],
                activeforeground=self.colors['bg_primary'],
                relief="flat", 
                cursor="hand2", 
                width=2,
                bd=0
            )
            remove_btn.grid(row=0, column=4, sticky="e", padx=(5, 5))
            
            # Add hover effects
            remove_btn.bind('<Enter>', lambda e, btn=remove_btn: self.on_remove_button_hover(btn, True))
            remove_btn.bind('<Leave>', lambda e, btn=remove_btn: self.on_remove_button_hover(btn, False))
            
            # Configure grid to push columns right
            file_frame.grid_columnconfigure(0, weight=1)  # filename expands
            file_frame.grid_columnconfigure(1, minsize=110)  # resolution
            file_frame.grid_columnconfigure(2, minsize=75)   # length
            file_frame.grid_columnconfigure(3, minsize=75)   # fps
            file_frame.grid_columnconfigure(4, minsize=28)   # ✕ button
            
            self.file_frames.append(file_frame)
            
            total_size += video_info['file_size_mb']
            total_duration += video_info['duration']
        
        # Update summary
        file_count = len(self.video_infos)
        summary_text = f"{file_count} files • {total_duration:.1f}s total • {total_size:.1f}MB total"
        self.file_summary_label.config(text=summary_text)
    

    
    def analyze_video(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                raise Exception("Could not open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Get file size
            file_size = os.path.getsize(self.video_path)
            file_size_mb = file_size / (1024 * 1024)
            
            self.video_info = {
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration,
                'file_size_mb': file_size_mb,
                'filename': os.path.basename(self.video_path)
            }
            
            cap.release()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not analyze video: {str(e)}")
    
    def update_file_info(self):
        if not self.video_info:
            return
            
        info_text = f"""File: {self.video_info['filename']}
Duration: {self.video_info['duration']:.2f} seconds
Resolution: {self.video_info['width']}x{self.video_info['height']}
FPS: {self.video_info['fps']:.2f}
Frames: {self.video_info['frame_count']}
Size: {self.video_info['file_size_mb']:.1f} MB"""
        
        self.file_info_text.config(state=tk.NORMAL)
        self.file_info_text.delete(1.0, tk.END)
        self.file_info_text.insert(1.0, info_text)
        self.file_info_text.config(state=tk.DISABLED)
    
    def process_videos(self):
        """Process all selected videos"""
        if not self.video_paths or self.is_processing:
            return
        if self.format_var.get() == "HAP" and not self.ensure_hap_or_prompt():
            return
        if not self.ffmpeg_available:
            self.show_ffmpeg_installation_prompt()
            return
        
        # Ask for output directory (same for single and multiple files)
        output_dir = filedialog.askdirectory(
            title="Select Output Directory for Looped Videos"
        )
        
        if not output_dir:
            return
        
        # Generate output paths for all files with normalized paths
        self.output_paths = []
        for video_info in self.video_infos:
            base_name = os.path.splitext(video_info['filename'])[0]
            extension = f".{self.format_var.get().lower()}"
            if self.format_var.get() == "HAP":
                extension = ".mov"  # HAP uses .mov extension
            
            output_path = os.path.join(output_dir, f"{base_name}_LOOPER{extension}")
            # Normalize path separators
            output_path = self.normalize_path(output_path)
            self.output_paths.append(output_path)
        
        self.current_processing_index = 0
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_videos_thread)
        thread.daemon = True
        thread.start()
    
    def process_videos_thread(self):
        """Process all videos in batch"""
        try:
            total_files = len(self.video_infos)
            successful_files = []
            failed_files = []
            
            for i, video_info in enumerate(self.video_infos):
                self.current_processing_index = i
                
                # Update status for current file
                current_file = video_info['filename']
                file_progress = (i / total_files) * 100
                self.update_status(f"📁 Processing {i+1}/{total_files}: {current_file}", 
                                 file_progress)
                
                # Process this video
                success = self.process_single_video(
                    video_info, 
                    self.output_paths[i], 
                    self.format_var.get()
                )
                
                if success:
                    successful_files.append(current_file)
                else:
                    failed_files.append(current_file)
            
            # Show completion summary
            self.update_status("🎉 BATCH PROCESSING COMPLETE!", 100)
            
            summary_message = f"Batch Processing Complete!\n\n"
            summary_message += f"✓ Successfully processed: {len(successful_files)} files\n"
            if failed_files:
                summary_message += f"✗ Failed to process: {len(failed_files)} files\n"
                summary_message += f"\nFailed files:\n" + "\n".join(failed_files)
            
            messagebox.showinfo("Batch Complete", summary_message)
            
        except Exception as e:
            self.update_status(f"❌ Batch processing error: {str(e)}", 0)
            messagebox.showerror("Error", f"Batch processing failed: {str(e)}")
        finally:
            self.is_processing = False
            self.process_button.config(state=tk.NORMAL)
    
    def process_single_video(self, video_info, output_path, output_format):
        """Process a single video file"""
        try:
            # Check HAP encoder availability if HAP format is selected
            if output_format == "HAP" and not self.ff_has_hap:
                messagebox.showerror(
                    "HAP Encoder Missing",
                    "Your FFmpeg build does not include HAP encoder.\n\n"
                    "Please install a full FFmpeg build with HAP support:\n"
                    "• Use the installer to get Gyan.FFmpeg.Full\n"
                    "• Or download ffmpeg-git-full.7z from Gyan.dev\n"
                    "• Extract and place ffmpeg.exe manually"
                )
                return False
            
            # Normalize input and output paths
            input_path = self.normalize_path(video_info['path'])
            output_path = self.normalize_path(output_path)
            
            print(f"Processing video: {input_path}")
            print(f"Output path: {output_path}")
            
            overlap_time = self.overlap_var.get()
            
            # Calculate overlap frames based on mode
            if self.overlap_mode.get() == "seconds":
                overlap_frames = int(overlap_time * video_info['fps'])
            else:
                # User input is already in frames
                overlap_frames = int(overlap_time)
            total_frames = video_info['frame_count']
            
            # Try the complex filter first
            success = self.try_complex_filter_for_file(
                input_path, output_path, overlap_frames, total_frames, output_format, video_info['fps']
            )
            
            if not success:
                # Fallback to simple loop
                success = self.try_simple_loop_for_file(
                    input_path, output_path, video_info['duration'], output_format
                )
                
            if not success:
                # Final fallback - just copy the video as-is
                success = self.try_basic_copy_for_file(
                    input_path, output_path, output_format
                )
            
            return success
                
        except Exception as e:
            print(f"Error processing {video_info['filename']}: {str(e)}")
            return False
    
    def build_filter_complex(self, overlap_frames, total_frames, fps=30):
        """Build the filter complex for creating a perfect loop with crossfade"""
        
        # Calculate overlap duration in seconds
        overlap_duration = overlap_frames / fps
        total_duration = total_frames / fps
        
        # Ensure overlap doesn't exceed video duration
        if overlap_duration >= total_duration:
            overlap_duration = total_duration * 0.1  # Use 10% of video as fallback
        
        # Calculate when to start the fade (end of video minus overlap)
        fade_start_time = total_duration - overlap_duration
        
        # Perfect Loop Technique - Your Description:
        # 1. Duplicate clip
        # 2. Trim duplicate so it starts X seconds before end of original  
        # 3. Shorten sequence to original length (no extra runtime)
        # 4. Move duplicate to beginning of timeline, under original
        # 5. Crossfade: Duplicate fades OUT (100% → 0%), Original visible (0% → 100%)
        
        # CORRECT IMPLEMENTATION - Following Your EXACT Instructions:
        # 1. Duplicate the clip ✓
        # 2. Trim duplicate so it begins X seconds BEFORE THE END (not beginning!)
        # 3. Shorten sequence to original length - X 
        # 4. Place duplicate at the START (not end!)
        # 5. Fade duplicate OUT over X seconds
        
        # Calculate the correct durations
        trim_start = total_duration - overlap_duration  # Start X seconds before end
        output_duration = total_duration - overlap_duration  # Shorter final length
        
        # Correct filter following your exact steps with fixes:
        # 1. Force exact frame alignment with fps filter
        # 2. Clamp fade fully to zero with color=black
        # 3. Shorten fade by 1 frame to ensure complete fade out
        frame_duration = 1.0 / fps
        fade_duration = overlap_duration - frame_duration
        
        filter_str = f"[0:v]fps={fps},trim=0:{output_duration},setpts=PTS-STARTPTS[base];[0:v]fps={fps},trim={trim_start}:{total_duration},setpts=PTS-STARTPTS,fade=t=out:st=0:d={fade_duration}:alpha=1:color=black[overlay];[base][overlay]overlay,format=yuv420p[outv]"
        
        return filter_str
    
    def try_complex_filter(self, overlap_frames, total_frames, output_format):
        """Try the complex filter method for creating loops"""
        try:
            # Build ffmpeg command for crossfade loop
            ffmpeg_cmd = self._ff(
                '-y',  # Overwrite output
                '-i', self.video_path,  # Input video
                '-filter_complex', self.build_filter_complex(overlap_frames, total_frames, 30),
                '-map', '[outv]',  # Map the output from filter complex
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',  # Ensure compatibility with H.264
                self.output_path
            )
            
            # Debug: Print the command
            print("FFmpeg command:", ' '.join(ffmpeg_cmd))
            
            # Execute ffmpeg command
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Monitor progress and capture error output
            stderr_output = []
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    # Parse progress from ffmpeg output
                    if 'time=' in output:
                        self.update_status("⚡ Rendering perfect loop...", 70)
                    elif 'frame=' in output:
                        self.update_status("🎬 Processing frames...", 50)
                    elif 'speed=' in output:
                        self.update_status("🚀 Encoding video...", 80)
            
            return_code = process.poll()
            if return_code != 0:
                print("Complex filter stderr:", '\n'.join(stderr_output))
            return return_code == 0
            
        except Exception as e:
            print(f"Complex filter failed: {e}")
            return False
    
    def try_simple_loop(self, output_format):
        """Try a simpler method using concatenation"""
        try:
            # Create a simple loop by duplicating the video
            # This creates a basic loop that can be played in a loop
            duration = self.video_info['duration']
            
            ffmpeg_cmd = self._ff(
                '-y',
                '-i', self.video_path,
                '-filter_complex', f'[0:v]loop=loop=1:size=1,trim=duration={duration*2}[outv]',
                '-map', '[outv]',
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',  # Ensure compatibility
                self.output_path
            )
            
            print("Simple loop command:", ' '.join(ffmpeg_cmd))
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stderr_output = []
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    if 'time=' in output:
                        self.update_status("⚡ Rendering simple loop...", 80)
                    elif 'frame=' in output:
                        self.update_status("🎬 Processing frames...", 60)
                    elif 'speed=' in output:
                        self.update_status("🚀 Encoding video...", 90)
            
            return_code = process.poll()
            if return_code != 0:
                print("Simple loop stderr:", '\n'.join(stderr_output))
            return return_code == 0
            
        except Exception as e:
            print(f"Simple loop failed: {e}")
            return False
    
    def try_basic_copy(self, output_format):
        """Try the most basic method - just copy the video"""
        try:
            # Simply copy the video without any processing
            # This ensures we can at least save the video in the desired format
            ffmpeg_cmd = self._ff(
                '-y',
                '-i', self.video_path,
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',
                self.output_path
            )
            
            print("Basic copy command:", ' '.join(ffmpeg_cmd))
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stderr_output = []
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    if 'time=' in output:
                        self.update_status("Copying video...", 90)
            
            return_code = process.poll()
            if return_code != 0:
                print("Basic copy stderr:", '\n'.join(stderr_output))
            return return_code == 0
            
        except Exception as e:
            print(f"Basic copy failed: {e}")
            return False
    
    def get_codec(self, format_type):
        """Get the appropriate codec for the output format"""
        if format_type == "HAP":
            return "hap"
        elif format_type == "MP4":
            return "libx264"
        else:
            return "libx264"
    
    def get_crf_value(self, output_format):
        """Get the CRF value for the output format"""
        if output_format == "MP4":
            return str(self.quality_var.get())
        else:
            return "18"  # Default for HAP
    
    def try_complex_filter_for_file(self, input_path, output_path, overlap_frames, total_frames, output_format, fps=30):
        """Try the complex filter method for a specific file"""
        try:
            # Set current video info for progress tracking
            self.current_video_duration = total_frames / fps
            self.current_video_frames = total_frames
            
            # Build ffmpeg command for crossfade loop
            ffmpeg_cmd = self._ff(
                '-y',  # Overwrite output
                '-i', input_path,  # Input video
                '-filter_complex', self.build_filter_complex(overlap_frames, total_frames, fps),
                '-map', '[outv]',  # Map the output from filter complex
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',  # Ensure compatibility with H.264
                output_path
            )
            
            # Debug: Print the exact command and filter being used
            print("=" * 60)
            print("DEBUGGING LOOP FILTER:")
            print("Input path:", input_path)
            print("Output path:", output_path)
            print("Overlap frames:", overlap_frames)
            print("Total frames:", total_frames)
            print("FPS:", fps)
            print("Filter complex:")
            print(self.build_filter_complex(overlap_frames, total_frames, fps))
            print("FFmpeg command:", ' '.join(ffmpeg_cmd))
            print("=" * 60)
            
            # Log FFmpeg detection results
            print(f"FFmpeg available: {self.ffmpeg_available}")
            if not self.ffmpeg_available:
                print("ERROR: FFmpeg not available - this should not happen!")
                return False
            
            # Execute ffmpeg command
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Monitor progress and capture error output
            stderr_output = []
            last_progress = 0
            
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    
                    # Parse actual progress from FFmpeg output
                    progress = self.parse_ffmpeg_progress(output)
                    if progress is not None and progress > last_progress:
                        last_progress = progress
                        self.update_status(f"🎬 Rendering perfect loop... {progress:.1f}%", progress)
                    elif 'time=' in output and progress is None:
                        # Fallback status updates
                        if 'frame=' in output:
                            self.update_status("🎬 Processing frames...", 30)
                        elif 'speed=' in output:
                            self.update_status("🚀 Encoding video...", 60)
            
            # Set to 100% when complete
            self.update_status("✅ Loop rendering complete!", 100)
            
            return_code = process.poll()
            if return_code != 0:
                print("Complex filter stderr:", '\n'.join(stderr_output))
                # Log actual FFmpeg errors for debugging
                error_output = '\n'.join(stderr_output)
                print(f"FFmpeg error details: {error_output}")
            return return_code == 0
            
        except Exception as e:
            print(f"Complex filter failed for {input_path}: {e}")
            return False
    
    def try_simple_loop_for_file(self, input_path, output_path, duration, output_format):
        """Try a simpler method for a specific file"""
        try:
            # Set current video info for progress tracking
            self.current_video_duration = duration * 2  # Double duration for loop
            self.current_video_frames = int(duration * 2 * 30)  # Estimate frames
            
            ffmpeg_cmd = self._ff(
                '-y',
                '-i', input_path,
                '-filter_complex', f'[0:v]loop=loop=1:size=1,trim=duration={duration*2}[outv]',
                '-map', '[outv]',
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',
                output_path
            )
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Monitor progress and capture error output
            stderr_output = []
            last_progress = 0
            
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    
                    # Parse actual progress from FFmpeg output
                    progress = self.parse_ffmpeg_progress(output)
                    if progress is not None and progress > last_progress:
                        last_progress = progress
                        self.update_status(f"🎬 Processing simple loop... {progress:.1f}%", progress)
                    elif 'time=' in output and progress is None:
                        # Fallback status updates
                        if 'frame=' in output:
                            self.update_status("🎬 Processing frames...", 30)
                        elif 'speed=' in output:
                            self.update_status("🚀 Encoding video...", 60)
            
            # Set to 100% when complete
            self.update_status("✅ Simple loop complete!", 100)
            
            return_code = process.poll()
            if return_code != 0:
                print("Simple loop stderr:", '\n'.join(stderr_output))
                # Log actual FFmpeg errors for debugging
                error_output = '\n'.join(stderr_output)
                print(f"FFmpeg error details: {error_output}")
            return return_code == 0
            
        except Exception as e:
            print(f"Simple loop failed for {input_path}: {e}")
            return False
    
    def try_basic_copy_for_file(self, input_path, output_path, output_format):
        """Try basic copy for a specific file"""
        try:
            # Get video duration for progress tracking
            cap = cv2.VideoCapture(input_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.current_video_duration = frame_count / fps if fps > 0 else 0
                self.current_video_frames = frame_count
                cap.release()
            else:
                self.current_video_duration = 0
                self.current_video_frames = 0
            
            ffmpeg_cmd = self._ff(
                '-y',
                '-i', input_path,
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                output_path
            )
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Monitor progress and capture error output
            stderr_output = []
            last_progress = 0
            
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    
                    # Parse actual progress from FFmpeg output
                    progress = self.parse_ffmpeg_progress(output)
                    if progress is not None and progress > last_progress:
                        last_progress = progress
                        self.update_status(f"📋 Copying video... {progress:.1f}%", progress)
                    elif 'time=' in output and progress is None:
                        # Fallback status updates
                        if 'frame=' in output:
                            self.update_status("🎬 Processing frames...", 20)
                        elif 'speed=' in output:
                            self.update_status("🚀 Encoding video...", 40)
            
            # Set to 100% when complete
            self.update_status("✅ Basic copy complete!", 100)
            
            return_code = process.poll()
            if return_code != 0:
                print("Basic copy stderr:", '\n'.join(stderr_output))
                # Log actual FFmpeg errors for debugging
                error_output = '\n'.join(stderr_output)
                print(f"FFmpeg error details: {error_output}")
            return return_code == 0
            
        except Exception as e:
            print(f"Basic copy failed for {input_path}: {e}")
            return False
    
    def update_status(self, message, progress):
        """Update status with thread-safe GUI updates"""
        def update():
            self.status_label.config(text=message)
            self.progress_var.set(progress)
            
            # Update custom progress bar
            if hasattr(self, 'progress_bar_fill') and hasattr(self, 'progress_label'):
                # Calculate width based on progress percentage
                total_width = self.progress_bar_frame.winfo_width()
                if total_width > 0:
                    fill_width = int((progress / 100.0) * total_width)
                    self.progress_bar_fill.config(width=fill_width)
                
                # Update percentage label
                self.progress_label.config(text=f"{progress:.1f}%")
            
            self.root.update_idletasks()
        self.root.after(0, update)
    
    def parse_ffmpeg_progress(self, line):
        """Parse FFmpeg progress output and return progress percentage"""
        try:
            # Look for time progress: time=00:00:15.00
            time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
            if time_match and self.current_video_duration > 0:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = min(95, (current_time / self.current_video_duration) * 100)
                return progress
            
            # Look for frame progress: frame= 1234
            frame_match = re.search(r'frame=\s*(\d+)', line)
            if frame_match and hasattr(self, 'current_video_frames') and self.current_video_frames > 0:
                current_frame = int(frame_match.group(1))
                progress = min(95, (current_frame / self.current_video_frames) * 100)
                return progress
                
        except Exception as e:
            print(f"Error parsing FFmpeg progress: {e}")
        
        return None
    
    def on_window_resize(self, event):
        """Handle window resize to update progress bar"""
        if hasattr(self, 'progress_bar_fill') and hasattr(self, 'progress_var'):
            progress = self.progress_var.get()
            total_width = self.progress_bar_frame.winfo_width()
            if total_width > 0:
                fill_width = int((progress / 100.0) * total_width)
                self.progress_bar_fill.config(width=fill_width)
    
    def load_settings(self):
        try:
            if os.path.exists('looper_settings.json'):
                with open('looper_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.overlap_var.set(settings.get('overlap_time', 1.0))
                    self.overlap_mode.set(settings.get('overlap_mode', 'seconds'))
                    self.format_var.set(settings.get('output_format', 'HAP'))
                    self.quality_var.set(settings.get('quality_crf', 18))
                    # Recent files functionality removed
                    
                    # Update UI based on loaded settings
                    if self.overlap_mode.get() == "frames":
                        self.overlap_toggle.config(text="FRAMES")
                        self.overlap_spinbox.config(from_=1, to=300, increment=1)
        except:
            pass
    
    def save_settings(self):
        settings = {
            'overlap_time': self.overlap_var.get(),
            'overlap_mode': self.overlap_mode.get(),
            'output_format': self.format_var.get(),
            'quality_crf': self.quality_var.get(),
            'recent_files': []  # Recent files functionality removed
        }
        
        try:
            with open('looper_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
        except:
            pass
    
    def add_to_recent_files(self, file_path):
        try:
            with open('looper_settings.json', 'r') as f:
                settings = json.load(f)
        except:
            settings = {'recent_files': []}
        
        recent_files = settings.get('recent_files', [])
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Keep only last 10
        recent_files = recent_files[:10]
        
        settings['recent_files'] = recent_files
        
        with open('looper_settings.json', 'w') as f:
            json.dump(settings, f)
        
        self.load_recent_files_list(recent_files)
    
    def load_recent_files_list(self, recent_files):
        self.recent_listbox.delete(0, tk.END)
        for file_path in recent_files:
            if os.path.exists(file_path):
                self.recent_listbox.insert(tk.END, os.path.basename(file_path))
    
    def get_recent_files_list(self):
        try:
            with open('looper_settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get('recent_files', [])
        except:
            return []
    
    def remove_file_by_index(self, index):
        """Remove file by index"""
        if 0 <= index < len(self.video_infos):
            # Remove from both lists
            del self.video_infos[index]
            del self.video_paths[index]
            
            # Update display
            self.update_file_display()
            
            # Disable process button if no files left
            if not self.video_infos:
                self.process_button.config(state=tk.DISABLED)
    
    def on_remove_button_hover(self, button, entering):
        """Handle hover effects for remove buttons"""
        if entering:
            button.config(bg=self.colors['accent_primary'])
        else:
            button.config(bg=self.colors['accent_secondary'])
    
    def on_file_double_click(self, event):
        """Handle double-click on file list to remove files"""
        selection = self.files_listbox.curselection()
        if selection and selection[0] < len(self.video_infos):
            # Remove from both lists
            del self.video_infos[selection[0]]
            del self.video_paths[selection[0]]
            
            # Update display
            self.update_file_display()
            
            # Disable process button if no files left
            if not self.video_infos:
                self.process_button.config(state=tk.DISABLED)
    
    def remove_selected_file(self):
        """Remove selected file from queue"""
        selection = self.files_listbox.curselection()
        if selection and selection[0] < len(self.video_infos):
            # Remove from both lists
            del self.video_infos[selection[0]]
            del self.video_paths[selection[0]]
            
            # Update display
            self.update_file_display()
            
            # Disable process button if no files left
            if not self.video_infos:
                self.process_button.config(state=tk.DISABLED)
    
    def load_recent_file(self, event):
        selection = self.recent_listbox.curselection()
        if selection:
            try:
                with open('looper_settings.json', 'r') as f:
                    settings = json.load(f)
                    recent_files = settings.get('recent_files', [])
                    if selection[0] < len(recent_files):
                        file_path = recent_files[selection[0]]
                        if os.path.exists(file_path):
                            self.video_paths = [file_path]
                            self.analyze_all_videos()
                            self.update_file_display()
                            self.process_button.config(state=tk.NORMAL)
            except:
                pass
    
    def update_status(self, message, progress):
        """Update status with thread-safe GUI updates"""
        def update():
            self.status_label.config(text=message)
            self.progress_var.set(progress)
            
            # Update custom progress bar
            if hasattr(self, 'progress_bar_fill') and hasattr(self, 'progress_label'):
                # Calculate width based on progress percentage
                total_width = self.progress_bar_frame.winfo_width()
                if total_width > 0:
                    fill_width = int((progress / 100.0) * total_width)
                    self.progress_bar_fill.config(width=fill_width)
                
                # Update percentage label
                self.progress_label.config(text=f"{progress:.1f}%")
            
            self.root.update_idletasks()
        self.root.after(0, update)

def main():
    # Try to use tkinterdnd2 for better drag and drop support
    try:
        import tkinterdnd2 as tkdnd
        root = tkdnd.TkinterDnD.Tk()
        print("✓ Using tkinterdnd2 for drag and drop support")
    except ImportError:
        root = tk.Tk()
        print("⚠️ Using standard Tkinter (limited drag and drop)")
    
    app = LooperApp(root)
    
    # Save settings on close
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
