# Looper - Perfect Video Loops

A lightweight Windows application for creating seamless video loops with automatic crossfade transitions.

## Features

- **Perfect Loops**: Automatically creates seamless video loops by overlapping the end with the beginning
- **Crossfade Transitions**: Smooth opacity transitions hide the "jump cut" at loop points
- **Multiple Formats**: Support for HAP (MOV) and MP4 output formats
- **Customizable Overlap**: Adjustable overlap time (0.1-10 seconds)
- **Video Analysis**: Displays detailed video information (duration, resolution, FPS, file size)
- **Recent Files**: Quick access to previously processed videos
- **Modern UI**: Futuristic dark theme with neon green accents

## Requirements

- Windows 10/11
- Python 3.7 or higher
- FFmpeg (for video processing)

## Installation

1. **Install Python**: Download and install Python from [python.org](https://python.org)
2. **Install FFmpeg**: Download FFmpeg from [ffmpeg.org](https://ffmpeg.org) and add it to your system PATH
3. **Run the application**: Double-click `run_looper.bat` to start

The batch file will automatically install required Python packages on first run.

## How It Works

Looper uses the VJ technique for creating perfect loops:

1. **Duplicate the clip**: Creates two copies of your video
2. **Overlap sections**: Overlaps the end of the first clip with the start of the second
3. **Crossfade transition**: Applies opacity fade between the overlapping sections
4. **Render loop**: Outputs only the length of the original clip with the blended transition

When the video loops, the crossfade creates a seamless transition instead of a hard cut.

## Usage

1. **Select Video**: Click "Select Video File" to choose your input video (MP4, MOV, AVI, MKV)
2. **Adjust Settings**: 
   - Set overlap time (recommended: 0.5-2 seconds)
   - Choose output format (HAP for VJ software, MP4 for general use)
3. **Create Loop**: Click "Create Perfect Loop" and choose output location
4. **Wait for Processing**: The app will show progress and notify when complete

## Tips

- **Overlap Time**: Longer overlaps create smoother transitions but may affect timing
- **HAP Format**: Use for VJ software like Resolume, VDMX, or TouchDesigner
- **MP4 Format**: Use for general playback or web sharing
- **File Size**: HAP files are larger but optimized for real-time playback

## Technical Details

- Uses OpenCV for video analysis
- FFmpeg for video processing and encoding
- Tkinter for the user interface
- Supports various input formats and codecs

## Troubleshooting

- **"Python not found"**: Install Python and ensure it's in your system PATH
- **"FFmpeg not found"**: Install FFmpeg and add it to your system PATH
- **Processing errors**: Check that your video file is not corrupted and has a supported format
- **Large file sizes**: HAP format creates larger files but is optimized for real-time playback

### FFmpeg Issues

If you're getting "FFmpeg processing failed" errors:

1. **Run the test script**: Double-click `test_ffmpeg.bat` to test FFmpeg functionality
2. **Check FFmpeg installation**: Run `check_ffmpeg.bat` to verify FFmpeg is properly installed
3. **Update FFmpeg**: Download the latest version from [ffmpeg.org](https://ffmpeg.org)
4. **Check codecs**: Ensure your FFmpeg build includes HAP and H.264 codecs
5. **Try different format**: Switch from HAP to MP4 if HAP codec is not available

### Common Solutions

- **"Codec not found"**: Install a full FFmpeg build with all codecs
- **"Filter complex error"**: The app will automatically try alternative methods
- **"Permission denied"**: Run as administrator or check file permissions
- **"Out of memory"**: Try processing smaller videos or reduce resolution

## License

This project is open source and available under the MIT License.
