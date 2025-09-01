# LOOPER v0.9 - Loop Mechanism Documentation

## Overview
This document captures the current working implementation of the video looping mechanism in LOOPER v0.9. This serves as a reference for restoration if the loop functionality breaks in future updates.

**Last Updated**: Current working version (after progress bar and UI improvements)
**Status**: ✅ WORKING

---

## Core Loop Implementation

### 1. Main Processing Flow

The loop processing follows this hierarchy (fallback system):

1. **Complex Filter Method** (Primary) - Perfect crossfade loops
2. **Simple Loop Method** (Fallback) - Basic video duplication
3. **Basic Copy Method** (Emergency) - Just copy the video

### 2. Complex Filter Method (Primary)

**File**: `looper.py` - `try_complex_filter_for_file()` method

**Purpose**: Creates perfect seamless loops with crossfade transitions

**Key Components**:

```python
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
    
    # Calculate the correct durations
    trim_start = total_duration - overlap_duration  # Start X seconds before end
    output_duration = total_duration - overlap_duration  # Shorter final length
    
    # Correct filter following exact steps:
    filter_str = f"[0:v]trim=0:{output_duration},setpts=PTS-STARTPTS[base];[0:v]trim={trim_start}:{total_duration},setpts=PTS-STARTPTS,fade=t=out:st=0:d={overlap_duration}:alpha=1[overlay];[base][overlay]overlay[outv]"
    
    return filter_str
```

**FFmpeg Command Structure**:
```python
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
```

**How It Works**:
1. **Duplicate clip**: Uses the same input twice in filter complex
2. **Trim duplicate**: Starts X seconds before the end of original
3. **Shorten sequence**: Reduces final length by overlap duration
4. **Place duplicate at start**: Overlays the trimmed duplicate at beginning
5. **Crossfade**: Duplicate fades OUT (100% → 0%), Original visible (0% → 100%)

### 3. Simple Loop Method (Fallback)

**File**: `looper.py` - `try_simple_loop_for_file()` method

**Purpose**: Creates basic loops when complex filter fails

**FFmpeg Command**:
```python
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
```

**How It Works**:
- Uses FFmpeg's `loop` filter to duplicate the video once
- Trims to double the original duration
- Creates a basic loop that can be played in a loop

### 4. Basic Copy Method (Emergency)

**File**: `looper.py` - `try_basic_copy_for_file()` method

**Purpose**: Ensures we can at least save the video in desired format

**FFmpeg Command**:
```python
ffmpeg_cmd = [
    'ffmpeg', '-y',
    '-i', input_path,
    '-c:v', self.get_codec(output_format),
    '-preset', 'fast',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    output_path
]
```

---

## Codec and Format Support

### Supported Output Formats

1. **HAP Format**:
   - Codec: `hap`
   - Extension: `.mov`
   - CRF: `18` (default)

2. **MP4 Format**:
   - Codec: `libx264`
   - Extension: `.mp4`
   - CRF: User-configurable (default: `18`)

### Codec Selection Logic

```python
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
```

---

## Overlap Configuration

### Overlap Modes

1. **Seconds Mode** (Default):
   - Range: 0.1 to 10.0 seconds
   - Increment: 0.1 seconds
   - Conversion: `overlap_frames = int(overlap_time * video_info['fps'])`

2. **Frames Mode**:
   - Range: 1 to 300 frames
   - Increment: 1 frame
   - Conversion: `overlap_time = current_frames / 30`

### Toggle Logic

```python
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
```

---

## Progress Tracking Implementation

### FFmpeg Progress Parsing

```python
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
```

### Status Updates

```python
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
```

---

## Video Analysis

### Video Properties Extraction

```python
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
```

---

## Error Handling and Fallbacks

### Processing Hierarchy

1. **Try Complex Filter**: Attempts perfect crossfade loop
2. **Fallback to Simple Loop**: If complex filter fails
3. **Emergency Basic Copy**: If all else fails, just copy the video

### Error Recovery

```python
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
```

---

## Batch Processing

### Multi-file Support

The application supports processing multiple files in sequence:

1. **Single File**: One video file
2. **Multiple Files**: Multiple selected video files
3. **Batch Folder**: All video files in a folder

### Batch Processing Logic

```python
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
```

---

## Settings and Persistence

### Settings Structure

```python
settings = {
    'overlap_time': self.overlap_var.get(),
    'overlap_mode': self.overlap_mode.get(),
    'output_format': self.format_var.get(),
    'quality_crf': self.quality_var.get(),
    'recent_files': self.get_recent_files_list()
}
```

### Settings File

- **File**: `looper_settings.json`
- **Location**: Same directory as `looper.py`
- **Format**: JSON

---

## Dependencies

### Required Python Packages

```python
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
import re
```

### External Dependencies

1. **FFmpeg**: Must be installed and accessible in PATH
2. **OpenCV**: For video analysis (`cv2`)
3. **Pillow**: For image processing (`PIL`)

---

## Troubleshooting Guide

### Common Issues

1. **FFmpeg Not Found**:
   - Ensure FFmpeg is installed and in system PATH
   - Test with: `ffmpeg -version`

2. **Complex Filter Fails**:
   - Falls back to simple loop method
   - Check FFmpeg version compatibility

3. **Progress Bar Not Updating**:
   - Verify FFmpeg output parsing
   - Check thread safety of GUI updates

4. **Video Analysis Fails**:
   - Ensure video file is not corrupted
   - Check if OpenCV can open the file

### Debug Information

The application prints debug information for:
- FFmpeg commands being executed
- Filter complex strings
- Error messages from FFmpeg
- Progress parsing results

---

## Version History

### v0.9 (Current Working Version)
- ✅ Unified color scheme
- ✅ Enhanced progress bar with real-time updates
- ✅ Improved FFmpeg progress parsing
- ✅ Better error handling and fallbacks
- ✅ Multi-file batch processing
- ✅ Settings persistence

### Previous Versions
- v0.8: Basic loop functionality
- v0.7: Initial crossfade implementation
- v0.6: Simple video duplication

---

## Restoration Instructions

If the loop mechanism breaks in future updates:

1. **Check this documentation** for the working implementation
2. **Restore the specific methods** mentioned above
3. **Test with known working video files**
4. **Verify FFmpeg compatibility**
5. **Check error logs** for specific failure points

### Key Methods to Restore

1. `build_filter_complex()` - Core loop algorithm
2. `try_complex_filter_for_file()` - Primary processing method
3. `try_simple_loop_for_file()` - Fallback method
4. `try_basic_copy_for_file()` - Emergency method
5. `parse_ffmpeg_progress()` - Progress tracking
6. `update_status()` - GUI updates

---

**Note**: This documentation should be updated whenever the loop mechanism is modified to ensure it reflects the current working implementation.
