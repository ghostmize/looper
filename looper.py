import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import json
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime
import tempfile
import shutil

class LooperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("◉ LOOPER v0.9 - Perfect Video Loops")
        self.root.geometry("950x800")
        self.root.configure(bg='#0a0a0f')
        
        # Define color scheme
        self.colors = {
            'bg_primary': '#0a0a0f',      # Dark background
            'bg_secondary': '#1a1a2a',    # Secondary background
            'bg_container': '#2a2a3a',    # Container background
            'cyan': '#08c3d9',            # Primary cyan
            'pink': '#ff007a',            # Primary pink
            'white': '#ffffff',           # White text
            'gray': '#666677'             # Gray text
        }
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        # Set window icon if available
        try:
            if os.path.exists('looper_icon.ico'):
                self.root.iconbitmap('looper_icon.ico')
        except:
            pass
        
        # Video file info - now supports multiple files
        self.video_paths = []  # List of video file paths
        self.video_infos = []  # List of video info dictionaries
        self.output_paths = []  # List of output paths
        self.current_processing_index = 0
        
        # Processing state
        self.is_processing = False
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        # Configure styles
        self.setup_styles()
        
        # Main container with gradient-like effect
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section - horizontal, classy, minimal
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Left side - Logo and title (horizontal layout)
        left_header = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        left_header.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Minimal title with icon
        title_container = tk.Frame(left_header, bg=self.colors['bg_primary'])
        title_container.pack(side=tk.LEFT)
        
        # Simple loop icon (minimal)
        self.create_minimal_logo(title_container)
        
        # Title and subtitle in horizontal layout
        text_container = tk.Frame(title_container, bg=self.colors['bg_primary'])
        text_container.pack(side=tk.LEFT, padx=(15, 0))
        
        title_label = tk.Label(
            text_container, 
            text="LOOPER", 
            font=("Consolas", 28, "bold"), 
            fg=self.colors['cyan'], 
            bg=self.colors['bg_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            text_container, 
            text=" • Perfect Video Loops", 
            font=("Consolas", 14), 
            fg=self.colors['white'], 
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
            fg=self.colors['white'], 
            bg=self.colors['bg_primary'],
            cursor="hand2"
        )
        self.ghosteam_label.pack(side=tk.RIGHT)
        
        separator_label = tk.Label(
            right_header, 
            text=" | ", 
            font=("Consolas", 12), 
            fg=self.colors['gray'], 
            bg=self.colors['bg_primary']
        )
        separator_label.pack(side=tk.RIGHT)
        
        version_label = tk.Label(
            right_header, 
            text="v0.9", 
            font=("Consolas", 12, "bold"), 
            fg=self.colors['pink'], 
            bg=self.colors['bg_primary']
        )
        version_label.pack(side=tk.RIGHT)
        
        # Add hover effect to Ghosteam
        def on_ghosteam_enter(e):
            self.ghosteam_label.config(fg=self.colors['pink'])
        def on_ghosteam_leave(e):
            self.ghosteam_label.config(fg=self.colors['white'])
        
        self.ghosteam_label.bind("<Enter>", on_ghosteam_enter)
        self.ghosteam_label.bind("<Leave>", on_ghosteam_leave)
        self.ghosteam_label.bind("<Button-1>", self.show_about)
        
        # Elegant separator line
        separator_frame = tk.Frame(header_frame, bg=self.colors['cyan'], height=2)
        separator_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Setup file selection section
        self.setup_file_section(main_frame)
        
        # Setup settings section
        self.setup_settings_section(main_frame)
        
        # Setup action buttons
        self.setup_action_section(main_frame)
        
        # Setup progress section
        self.setup_progress_section(main_frame)
        
        # Setup recent files section
        self.setup_recent_files_section(main_frame)
    
    def setup_styles(self):
        """Setup custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
                # Configure futuristic combobox style
        style.configure('Futuristic.TCombobox',
                        fieldbackground=self.colors['bg_secondary'],
                        background=self.colors['cyan'],
                        foreground=self.colors['cyan'],
                        borderwidth=1,
                        relief='flat',
                        focuscolor=self.colors['cyan'])
        
                # Configure futuristic progressbar
        style.configure('Futuristic.Horizontal.TProgressbar',
                        background=self.colors['cyan'],
                        troughcolor=self.colors['bg_container'],
                        borderwidth=0,
                        lightcolor=self.colors['cyan'],
                        darkcolor=self.colors['cyan'])
    
    def setup_logo(self, parent):
        """Setup logo if available"""
        try:
            if os.path.exists('looper_logo.png'):
                from PIL import Image, ImageTk
                # Load and resize logo
                logo_img = Image.open('looper_logo.png')
                logo_img = logo_img.resize((64, 64), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = tk.Label(
                    parent,
                    image=self.logo_photo,
                    bg='#0a0a0f'
                )
                logo_label.pack(side=tk.LEFT)
        except Exception as e:
            # If logo loading fails, create a simple geometric logo
            self.create_simple_logo(parent)
    
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
                         outline='#00ffaa', width=3)
        
        # Inner infinity symbol
        canvas.create_oval(center-10, center-5, center, center+5, outline='#ffffff', width=2)
        canvas.create_oval(center, center-5, center+10, center+5, outline='#ffffff', width=2)
    
    def create_futuristic_button(self, parent, text, command, bg_color='#1a1a2a', fg_color='#00ffaa', hover_color='#00ffaa'):
        """Create a futuristic-styled button with hover effects"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Consolas", 10, "bold"),
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground='#000000',
            relief="flat",
            padx=20,
            pady=12,
            cursor="hand2",
            bd=1,
            highlightbackground=hover_color,
            highlightthickness=1
        )
        
        # Add hover effects
        def on_enter(e):
            button.config(bg=hover_color, fg='#000000')
        
        def on_leave(e):
            button.config(bg=bg_color, fg=fg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def create_minimal_logo(self, parent):
        """Create a minimal geometric logo"""
        canvas = tk.Canvas(parent, width=40, height=40, bg=self.colors['bg_primary'], highlightthickness=0)
        canvas.pack(side=tk.LEFT)
        
        # Simple loop circle with modern styling
        center = 20
        radius = 15
        
        # Main loop circle
        canvas.create_oval(center-radius, center-radius, center+radius, center+radius, 
                         outline=self.colors['cyan'], width=3)
        
        # Inner accent
        canvas.create_oval(center-8, center-8, center+8, center+8, 
                         outline=self.colors['pink'], width=2)
    
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
            text="LOOPER v0.9",
            font=("Consolas", 18, "bold"),
            fg=self.colors['cyan'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # Description
        desc_label = tk.Label(
            main_container,
            text="This is a free tool made by",
            font=("Consolas", 12),
            fg=self.colors['white'],
            bg=self.colors['bg_primary']
        )
        desc_label.pack()
        
        # Clickable Ghosteam link
        ghosteam_link = tk.Label(
            main_container,
            text="Ghosteam",
            font=("Consolas", 12, "bold"),
            fg=self.colors['pink'],
            bg=self.colors['bg_primary'],
            cursor="hand2"
        )
        ghosteam_link.pack(pady=(5, 15))
        
        def open_website(e):
            import webbrowser
            webbrowser.open("https://www.ghosteaminc.com")
        
        def on_link_enter(e):
            ghosteam_link.config(fg=self.colors['cyan'])
        def on_link_leave(e):
            ghosteam_link.config(fg=self.colors['pink'])
        
        ghosteam_link.bind("<Button-1>", open_website)
        ghosteam_link.bind("<Enter>", on_link_enter)
        ghosteam_link.bind("<Leave>", on_link_leave)
        
        # Contact info
        contact_label = tk.Label(
            main_container,
            text="Contact via our shop for any requests",
            font=("Consolas", 10),
            fg=self.colors['gray'],
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
            fg=self.colors['white'],
            activebackground=self.colors['cyan'],
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
            fg=self.colors['cyan'],
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
        
        # Create buttons that fill horizontal space
        self.single_file_button = self.create_futuristic_button(
            button_container, "SINGLE FILE", self.select_single_file, 
            bg_color=self.colors['bg_container'], fg_color=self.colors['cyan'], hover_color=self.colors['cyan']
        )
        self.single_file_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.multi_file_button = self.create_futuristic_button(
            button_container, "MULTIPLE FILES", self.select_multiple_files,
            bg_color=self.colors['bg_container'], fg_color=self.colors['pink'], hover_color=self.colors['pink']
        )
        self.multi_file_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        
        self.batch_folder_button = self.create_futuristic_button(
            button_container, "BATCH FOLDER", self.select_batch_folder,
            bg_color=self.colors['bg_container'], fg_color=self.colors['white'], hover_color=self.colors['white']
        )
        self.batch_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        # File list display with elegant styling
        list_header = tk.Label(
            file_inner,
            text="▸ SELECTED FILES",
            font=("Consolas", 10, "bold"),
            fg='#44ffaa',
            bg='#111122'
        )
        list_header.pack(anchor='w', pady=(15, 8))
        
        # Files listbox with futuristic styling
        listbox_container = tk.Frame(file_inner, bg='#1a1a2a', relief='solid', bd=1)
        listbox_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(listbox_container, bg='#1a1a2a')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.files_listbox = tk.Listbox(
            listbox_frame,
            font=("Consolas", 9),
            bg='#1a1a2a',
            fg='#00ffaa',
            selectbackground='#00ffaa',
            selectforeground='#000000',
            relief="flat",
            height=4,
            highlightthickness=0,
            activestyle='none'
        )
        
        scrollbar = tk.Scrollbar(
            listbox_frame, 
            orient=tk.VERTICAL, 
            command=self.files_listbox.yview,
            bg='#2a2a3a',
            troughcolor='#1a1a2a',
            activebackground='#00ffaa'
        )
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File summary with elegant styling
        self.file_summary_label = tk.Label(
            file_inner,
            text="◦ No files selected",
            font=("Consolas", 9),
            fg='#666677',
            bg='#111122'
        )
        self.file_summary_label.pack(anchor='w')
    
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
            fg=self.colors['cyan'],
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
        settings_row.pack(fill=tk.X, padx=15, pady=12)
        
        # Left side - Crossfade Duration
        left_settings = tk.Frame(settings_row, bg=self.colors['bg_container'])
        left_settings.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            left_settings,
            text="CROSSFADE DURATION",
            font=("Consolas", 11, "bold"),
            fg=self.colors['pink'],
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
            fg=self.colors['cyan'],
            insertbackground=self.colors['cyan'],
            relief="flat",
            width=6,
            bd=1,
            buttonbackground=self.colors['cyan'],
            selectbackground=self.colors['cyan'],
            selectforeground=self.colors['bg_primary']
        )
        self.overlap_spinbox.pack(side=tk.LEFT)
        
        # Toggle button for seconds/frames
        self.overlap_toggle = tk.Button(
            spinbox_container,
            text="SEC",
            command=self.toggle_overlap_mode,
            font=("Consolas", 9, "bold"),
            bg=self.colors['cyan'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['pink'],
            activeforeground=self.colors['bg_primary'],
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2"
        )
        self.overlap_toggle.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separator
        separator = tk.Frame(settings_row, bg=self.colors['pink'], width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Right side - Output Format
        right_settings = tk.Frame(settings_row, bg=self.colors['bg_container'])
        right_settings.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            right_settings,
            text="OUTPUT FORMAT",
            font=("Consolas", 11, "bold"),
            fg=self.colors['pink'],
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
            bg=self.colors['pink'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['cyan'],
            activeforeground=self.colors['bg_primary'],
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2"
        )
        
        # Bind format change to show/hide settings button
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # Check initial format and show button if needed
        self.check_initial_format()
    
    def setup_action_section(self, main_frame):
        """Setup the action buttons section"""
        # Action section with futuristic design
        action_section = tk.Frame(main_frame, bg='#0a0a0f')
        action_section.pack(pady=(0, 15))
        
        # Main process button - vibrant and modern
        self.process_button = tk.Button(
            action_section,
            text="⚡ GENERATE PERFECT LOOPS ⚡",
            command=self.process_videos,
            font=("Consolas", 18, "bold"),
            bg=self.colors['cyan'],
            fg='#000000',
            activebackground=self.colors['pink'],
            activeforeground='#000000',
            disabledforeground='#000000',
            relief="flat",
            bd=0,
            padx=60,
            pady=25,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.process_button.pack(pady=15)
        
        # Enhanced hover effect with color transitions
        def on_button_enter(e):
            if self.process_button['state'] != 'disabled':
                self.process_button.config(
                    bg=self.colors['pink'],
                    fg='#000000',
                    relief="raised",
                    bd=3
                )
                # Add a subtle glow effect
                self.process_button.config(highlightthickness=2, highlightbackground=self.colors['pink'])
        
        def on_button_leave(e):
            if self.process_button['state'] != 'disabled':
                self.process_button.config(
                    bg=self.colors['cyan'],
                    fg='#000000',
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
        else:
            self.settings_button.pack_forget()
    
    def check_initial_format(self):
        """Check initial format and show settings button if needed"""
        if self.format_var.get() == "MP4":
            self.settings_button.pack(side=tk.LEFT)
    
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
            fg=self.colors['cyan'],
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
            fg=self.colors['pink'],
            bg=self.colors['bg_secondary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            slider_inner,
            textvariable=self.quality_var,
            font=("Consolas", 11, "bold"),
            fg=self.colors['cyan'],
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
            fg=self.colors['white'],
            highlightthickness=0,
            troughcolor=self.colors['bg_container'],
            activebackground=self.colors['cyan'],
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
            fg=self.colors['cyan'],
            bg=self.colors['bg_primary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            indicators_frame,
            text="Small File",
            font=("Consolas", 8),
            fg=self.colors['gray'],
            bg=self.colors['bg_primary']
        ).pack(side=tk.RIGHT)
        
        # Close button
        close_button = tk.Button(
            main_container,
            text="Apply",
            command=quality_window.destroy,
            font=("Consolas", 10, "bold"),
            bg=self.colors['cyan'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['pink'],
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
        progress_section = tk.Frame(main_frame, bg='#0a0a0f')
        progress_section.pack(fill=tk.X, pady=(0, 15))
        
        # Section header
        progress_header = tk.Label(
            progress_section,
            text="◦ PROCESSING STATUS",
            font=("Consolas", 14, "bold"),
            fg='#00ffaa',
            bg='#0a0a0f'
        )
        progress_header.pack(anchor='w', pady=(0, 15))
        
        # Progress container
        progress_container = tk.Frame(progress_section, bg='#112211', relief='solid', bd=1)
        progress_container.pack(fill=tk.X, padx=5)
        
        # Inner container
        progress_inner = tk.Frame(progress_container, bg='#112211')
        progress_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Progress bar with ultra-modern styling
        self.progress_var = tk.DoubleVar()
        progress_container = tk.Frame(progress_inner, bg=self.colors['bg_primary'], padx=2, pady=2)
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_container,
            variable=self.progress_var,
            maximum=100,
            length=500,
            mode='determinate',
            style='Futuristic.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, padx=1, pady=1)
        
        # Status label with terminal styling
        self.status_label = tk.Label(
            progress_inner,
            text="◦ SYSTEM READY - AWAITING INPUT ◦",
            font=("Consolas", 10),
            fg='#44ffaa',
            bg='#112211'
        )
        self.status_label.pack()
    
    def setup_recent_files_section(self, main_frame):
        """Setup the recent files section"""
        # Recent files section with futuristic design
        recent_section = tk.Frame(main_frame, bg='#0a0a0f')
        recent_section.pack(fill=tk.BOTH, expand=True)
        
        # Section header
        recent_header = tk.Label(
            recent_section,
            text="◦ RECENT FILES",
            font=("Consolas", 14, "bold"),
            fg='#00ffaa',
            bg='#0a0a0f'
        )
        recent_header.pack(anchor='w', pady=(0, 15))
        
        # Recent files container
        recent_container = tk.Frame(recent_section, bg='#112222', relief='solid', bd=1)
        recent_container.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Inner container
        recent_inner = tk.Frame(recent_container, bg='#112222')
        recent_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Instructions
        recent_instruction = tk.Label(
            recent_inner,
            text="▸ DOUBLE-CLICK TO RELOAD",
            font=("Consolas", 9),
            fg='#44ffaa',
            bg='#112222'
        )
        recent_instruction.pack(anchor='w', pady=(0, 8))
        
        # Recent files listbox
        self.recent_listbox = tk.Listbox(
            recent_inner,
            font=("Consolas", 10),
            bg='#1a1a2a',
            fg='#00ffaa',
            selectbackground='#00ffaa',
            selectforeground='#000000',
            relief="flat",
            activestyle='none',
            highlightthickness=0
        )
        self.recent_listbox.pack(fill=tk.BOTH, expand=True)
        self.recent_listbox.bind('<Double-Button-1>', self.load_recent_file)
        
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
            self.video_paths = [file_path]
            self.analyze_all_videos()
            self.update_file_display()
            self.process_button.config(state=tk.NORMAL)
            self.add_to_recent_files(file_path)
    
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
            self.video_paths = list(file_paths)
            self.analyze_all_videos()
            self.update_file_display()
            self.process_button.config(state=tk.NORMAL)
            # Add all files to recent files
            for file_path in file_paths:
                self.add_to_recent_files(file_path)
    
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
                self.video_paths = sorted(video_files)  # Sort for consistent order
                self.analyze_all_videos()
                self.update_file_display()
                self.process_button.config(state=tk.NORMAL)
                # Add all files to recent files
                for file_path in video_files:
                    self.add_to_recent_files(file_path)
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
        # Clear the listbox
        self.files_listbox.delete(0, tk.END)
        
        if not self.video_infos:
            self.file_summary_label.config(text="No valid video files selected")
            return
        
        # Add files to listbox
        total_size = 0
        total_duration = 0
        
        for i, video_info in enumerate(self.video_infos):
            # Format: "filename (duration, size)"
            display_text = f"{video_info['filename']} ({video_info['duration']:.1f}s, {video_info['file_size_mb']:.1f}MB)"
            self.files_listbox.insert(tk.END, display_text)
            
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
        
        # For single file, ask for specific output path
        if len(self.video_paths) == 1:
            # Determine correct extension
            if self.format_var.get() == "HAP":
                extension = "mov"
                file_desc = "HAP (MOV) files"
            else:
                extension = self.format_var.get().lower()
                file_desc = f"{self.format_var.get()} files"
            
            output_path = filedialog.asksaveasfilename(
                title="Save Looped Video",
                defaultextension=f".{extension}",
                filetypes=[
                    (file_desc, f"*.{extension}"),
                    ("All files", "*.*")
                ]
            )
            
            if not output_path:
                return
            
            # Ensure correct extension
            if self.format_var.get() == "HAP" and not output_path.lower().endswith('.mov'):
                output_path = os.path.splitext(output_path)[0] + '.mov'
            
            self.output_paths = [output_path]
        else:
            # For multiple files, ask for output directory
            output_dir = filedialog.askdirectory(
                title="Select Output Directory for Batch Processing"
            )
            
            if not output_dir:
                return
            
            # Generate output paths for all files
            self.output_paths = []
            for video_info in self.video_infos:
                base_name = os.path.splitext(video_info['filename'])[0]
                extension = f".{self.format_var.get().lower()}"
                if self.format_var.get() == "HAP":
                    extension = ".mov"  # HAP uses .mov extension
                
                output_path = os.path.join(output_dir, f"{base_name}_loop{extension}")
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
                self.update_status(f"Processing {i+1}/{total_files}: {current_file}", 
                                 (i / total_files) * 100)
                
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
            self.update_status("BATCH PROCESSING COMPLETE", 100)
            
            summary_message = f"Batch Processing Complete!\n\n"
            summary_message += f"✓ Successfully processed: {len(successful_files)} files\n"
            if failed_files:
                summary_message += f"✗ Failed to process: {len(failed_files)} files\n"
                summary_message += f"\nFailed files:\n" + "\n".join(failed_files)
            
            messagebox.showinfo("Batch Complete", summary_message)
            
        except Exception as e:
            self.update_status(f"Batch processing error: {str(e)}", 0)
            messagebox.showerror("Error", f"Batch processing failed: {str(e)}")
        finally:
            self.is_processing = False
            self.process_button.config(state=tk.NORMAL)
    
    def process_single_video(self, video_info, output_path, output_format):
        """Process a single video file"""
        try:
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
                video_info['path'], output_path, overlap_frames, total_frames, output_format, video_info['fps']
            )
            
            if not success:
                # Fallback to simple loop
                success = self.try_simple_loop_for_file(
                    video_info['path'], output_path, video_info['duration'], output_format
                )
                
            if not success:
                # Final fallback - just copy the video as-is
                success = self.try_basic_copy_for_file(
                    video_info['path'], output_path, output_format
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
        
        # Create a simpler, more robust filter that works better with H.264
        # This creates a seamless loop by duplicating the video and crossfading
        filter_str = f"""[0:v]trim=0:{total_duration},setpts=PTS-STARTPTS[v1];
[0:v]trim=0:{total_duration},setpts=PTS-STARTPTS[v2];
[v1][v2]xfade=transition=fade:duration={overlap_duration}:offset={total_duration-overlap_duration}[outv]"""
        
        return filter_str
    
    def try_complex_filter(self, overlap_frames, total_frames, output_format):
        """Try the complex filter method for creating loops"""
        try:
            # Build ffmpeg command for crossfade loop
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-i', self.video_path,  # Input video
                '-filter_complex', self.build_filter_complex(overlap_frames, total_frames, 30),
                '-map', '[outv]',  # Map the output from filter complex
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',  # Ensure compatibility with H.264
                self.output_path
            ]
            
            # Debug: Print the command
            print("FFmpeg command:", ' '.join(ffmpeg_cmd))
            
            # Execute ffmpeg command
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
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
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', self.video_path,
                '-filter_complex', f'[0:v]loop=loop=1:size=1,trim=duration={duration*2}[outv]',
                '-map', '[outv]',
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',  # Ensure compatibility
                self.output_path
            ]
            
            print("Simple loop command:", ' '.join(ffmpeg_cmd))
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
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
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', self.video_path,
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',
                self.output_path
            ]
            
            print("Basic copy command:", ' '.join(ffmpeg_cmd))
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
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
            # Build ffmpeg command for crossfade loop
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-i', input_path,  # Input video
                '-filter_complex', self.build_filter_complex(overlap_frames, total_frames, fps),
                '-map', '[outv]',  # Map the output from filter complex
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',  # Ensure compatibility with H.264
                output_path
            ]
            
            # Execute ffmpeg command
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
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
                        self.update_status("Rendering loop...", 70)
            
            return_code = process.poll()
            if return_code != 0:
                print("Complex filter stderr:", '\n'.join(stderr_output))
            return return_code == 0
            
        except Exception as e:
            print(f"Complex filter failed for {input_path}: {e}")
            return False
    
    def try_simple_loop_for_file(self, input_path, output_path, duration, output_format):
        """Try a simpler method for a specific file"""
        try:
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-filter_complex', f'[0:v]loop=loop=1:size=1,trim=duration={duration*2}[outv]',
                '-map', '[outv]',
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', self.get_crf_value(output_format),
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitor progress and capture error output
            stderr_output = []
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    if 'time=' in output:
                        self.update_status("Processing simple loop...", 50)
            
            return_code = process.poll()
            if return_code != 0:
                print("Simple loop stderr:", '\n'.join(stderr_output))
            return return_code == 0
            
        except Exception as e:
            print(f"Simple loop failed for {input_path}: {e}")
            return False
    
    def try_basic_copy_for_file(self, input_path, output_path, output_format):
        """Try basic copy for a specific file"""
        try:
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', self.get_codec(output_format),
                '-preset', 'fast',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitor progress and capture error output
            stderr_output = []
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stderr_output.append(output)
                    if 'time=' in output:
                        self.update_status("📋 Copying video...", 30)
                    elif 'frame=' in output:
                        self.update_status("🎬 Processing frames...", 20)
                    elif 'speed=' in output:
                        self.update_status("🚀 Encoding video...", 40)
            
            return_code = process.poll()
            if return_code != 0:
                print("Basic copy stderr:", '\n'.join(stderr_output))
            return return_code == 0
            
        except Exception as e:
            print(f"Basic copy failed for {input_path}: {e}")
            return False
    
    def update_status(self, message, progress):
        """Update status with thread-safe GUI updates"""
        def update():
            self.status_label.config(text=message)
            self.progress_var.set(progress)
            self.root.update_idletasks()
        self.root.after(0, update)
    
    def load_settings(self):
        try:
            if os.path.exists('looper_settings.json'):
                with open('looper_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.overlap_var.set(settings.get('overlap_time', 1.0))
                    self.overlap_mode.set(settings.get('overlap_mode', 'seconds'))
                    self.format_var.set(settings.get('output_format', 'HAP'))
                    self.quality_var.set(settings.get('quality_crf', 18))
                    self.load_recent_files_list(settings.get('recent_files', []))
                    
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
            'recent_files': self.get_recent_files_list()
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

def main():
    root = tk.Tk()
    app = LooperApp(root)
    
    # Save settings on close
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
