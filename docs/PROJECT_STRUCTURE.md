# Looper Project Structure

## Overview
Looper is a lightweight Windows application for creating perfect video loops with automatic crossfade transitions. It's designed specifically for VJs and video artists who need seamless looping videos.

## File Structure

```
Looper/
├── looper.py              # Main application (GUI and core functionality)
├── launch_looper.py       # Launcher with dependency checking
├── requirements.txt       # Python dependencies
├── run_looper.bat         # Main batch file to run the application
├── setup.bat             # Setup script for first-time installation
├── check_ffmpeg.bat      # FFmpeg installation checker
├── README.md             # User documentation
└── PROJECT_STRUCTURE.md  # This file
```

## Core Components

### 1. Main Application (`looper.py`)
- **GUI**: Modern, futuristic interface with dark theme and neon green accents
- **Video Analysis**: Uses OpenCV to extract video properties (duration, FPS, resolution, etc.)
- **Loop Processing**: Implements the VJ technique for perfect loops using FFmpeg
- **Settings Management**: Saves/loads user preferences and recent files
- **Preview Feature**: Visual representation of how the loop will work

### 2. Launcher (`launch_looper.py`)
- **Dependency Checking**: Verifies Python, required packages, and FFmpeg
- **Auto-Installation**: Automatically installs missing Python packages
- **Error Handling**: Provides clear error messages for missing dependencies

### 3. Batch Files
- **`run_looper.bat`**: Main entry point, checks dependencies and launches the app
- **`setup.bat`**: First-time setup script for complete installation
- **`check_ffmpeg.bat`**: Standalone FFmpeg verification tool

## Key Features

### Video Processing
- **Input Formats**: MP4, MOV, AVI, MKV
- **Output Formats**: HAP (for VJ software), MP4 (general use)
- **Loop Technique**: 
  1. Duplicate the video clip
  2. Overlap end of first clip with start of second
  3. Apply crossfade transition in overlap region
  4. Render only original clip length

### User Interface
- **Modern Design**: Dark theme with neon green accents
- **File Information**: Displays detailed video properties
- **Recent Files**: Quick access to previously processed videos
- **Preview Window**: Visual representation of loop timing
- **Progress Tracking**: Real-time processing status

### Technical Implementation
- **OpenCV**: Video analysis and frame extraction
- **FFmpeg**: Video processing and encoding
- **Tkinter**: Cross-platform GUI framework
- **Threading**: Non-blocking video processing
- **JSON**: Settings and recent files storage

## Dependencies

### Required Software
- **Python 3.7+**: Core runtime
- **FFmpeg**: Video processing engine

### Python Packages
- **tkinter**: GUI framework (usually included with Python)
- **opencv-python**: Video analysis
- **Pillow**: Image processing
- **numpy**: Numerical operations

## Usage Workflow

1. **Setup**: Run `setup.bat` for first-time installation
2. **Launch**: Double-click `run_looper.bat` or run `python launch_looper.py`
3. **Select Video**: Choose input video file
4. **Configure**: Set overlap time and output format
5. **Preview**: Optional preview of loop timing
6. **Process**: Create the perfect loop
7. **Export**: Save in desired format

## Architecture

The application follows a simple MVC-like pattern:
- **Model**: Video data and processing logic
- **View**: Tkinter GUI components
- **Controller**: Event handlers and user interaction

## Error Handling

- **Dependency Checks**: Automatic verification of required software
- **File Validation**: Ensures video files are valid and supported
- **Processing Errors**: Graceful handling of FFmpeg failures
- **User Feedback**: Clear error messages and status updates

## Future Enhancements

Potential improvements for future versions:
- **Batch Processing**: Multiple video processing
- **Advanced Transitions**: Different transition types
- **Audio Support**: Audio loop synchronization
- **Plugin System**: Custom transition effects
- **Cloud Processing**: Remote video processing
- **Mobile App**: iOS/Android companion app

