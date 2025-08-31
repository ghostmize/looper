#!/usr/bin/env python3
"""
FFmpeg Debug Script for Looper
Helps debug specific FFmpeg issues with video processing
"""

import subprocess
import sys
import os
import json

def get_video_info(video_path):
    """Get detailed video information using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error getting video info: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception getting video info: {e}")
        return None

def test_basic_ffmpeg_operations(video_path):
    """Test basic FFmpeg operations on the video"""
    print(f"\nTesting basic FFmpeg operations on: {os.path.basename(video_path)}")
    
    # Test 1: Basic info extraction
    print("\n1. Testing basic info extraction...")
    try:
        cmd = ['ffmpeg', '-i', video_path, '-f', 'null', '-']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✓ Basic info extraction successful")
        else:
            print("✗ Basic info extraction failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Exception in basic info extraction: {e}")
    
    # Test 2: Simple copy
    print("\n2. Testing simple copy...")
    try:
        output_path = "test_copy.mp4"
        cmd = ['ffmpeg', '-y', '-i', video_path, '-c:v', 'libx264', '-preset', 'fast', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✓ Simple copy successful")
            os.remove(output_path)
        else:
            print("✗ Simple copy failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Exception in simple copy: {e}")
    
    # Test 3: Filter complex test
    print("\n3. Testing filter complex...")
    try:
        output_path = "test_filter.mp4"
        filter_str = "[0:v]trim=0:2,setpts=PTS-STARTPTS[outv]"
        cmd = ['ffmpeg', '-y', '-i', video_path, '-filter_complex', filter_str, 
               '-map', '[outv]', '-c:v', 'libx264', '-preset', 'fast', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✓ Filter complex successful")
            os.remove(output_path)
        else:
            print("✗ Filter complex failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Exception in filter complex: {e}")

def test_loop_operations(video_path):
    """Test loop-specific operations"""
    print(f"\nTesting loop operations on: {os.path.basename(video_path)}")
    
    # Test 1: Simple loop filter
    print("\n1. Testing simple loop filter...")
    try:
        output_path = "test_loop.mp4"
        cmd = ['ffmpeg', '-y', '-i', video_path, 
               '-filter_complex', '[0:v]loop=loop=1:size=1[outv]',
               '-map', '[outv]', '-c:v', 'libx264', '-preset', 'fast', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✓ Simple loop filter successful")
            os.remove(output_path)
        else:
            print("✗ Simple loop filter failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Exception in simple loop filter: {e}")
    
    # Test 2: Xfade test
    print("\n2. Testing xfade filter...")
    try:
        output_path = "test_xfade.mp4"
        filter_str = "[0:v][0:v]xfade=transition=fade:duration=0.5:offset=1.0[outv]"
        cmd = ['ffmpeg', '-y', '-i', video_path, '-i', video_path,
               '-filter_complex', filter_str, '-map', '[outv]', 
               '-c:v', 'libx264', '-preset', 'fast', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✓ Xfade filter successful")
            os.remove(output_path)
        else:
            print("✗ Xfade filter failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Exception in xfade filter: {e}")
    
    # Test 3: HAP format test
    print("\n3. Testing HAP format...")
    try:
        output_path = "test_hap.mov"  # HAP uses .mov extension
        cmd = ['ffmpeg', '-y', '-i', video_path, '-c:v', 'hap', '-preset', 'fast', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✓ HAP format successful")
            os.remove(output_path)
        else:
            print("✗ HAP format failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Exception in HAP format: {e}")
    
    # Test 4: Perfect loop test
    print("\n4. Testing perfect loop technique...")
    try:
        output_path = "test_perfect_loop.mp4"
        # Test with 2 second overlap on a 20 second video
        filter_str = "[0:v]trim=0:20,setpts=PTS-STARTPTS[original];[0:v]trim=0:20,setpts=PTS-STARTPTS[copy];[original][copy]xfade=transition=fade:duration=2:offset=18,trim=duration=20[outv]"
        cmd = ['ffmpeg', '-y', '-i', video_path, '-filter_complex', filter_str, '-map', '[outv]', '-c:v', 'libx264', '-preset', 'fast', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✓ Perfect loop technique successful")
            # Check the duration of the output
            duration_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', output_path]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, timeout=30)
            if duration_result.returncode == 0:
                duration = float(duration_result.stdout.strip())
                print(f"  Output duration: {duration:.2f} seconds (should be ~20.00)")
            os.remove(output_path)
        else:
            print("✗ Perfect loop technique failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Exception in perfect loop technique: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_ffmpeg.py <video_file>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"Error: File {video_path} does not exist")
        sys.exit(1)
    
    print("FFmpeg Debug Script for Looper")
    print("=" * 40)
    
    # Get video info
    print(f"\nAnalyzing video: {video_path}")
    video_info = get_video_info(video_path)
    
    if video_info:
        print("✓ Video info extracted successfully")
        if 'streams' in video_info and video_info['streams']:
            video_stream = video_info['streams'][0]
            print(f"Codec: {video_stream.get('codec_name', 'Unknown')}")
            print(f"Resolution: {video_stream.get('width', 'Unknown')}x{video_stream.get('height', 'Unknown')}")
            print(f"Duration: {video_info.get('format', {}).get('duration', 'Unknown')} seconds")
    else:
        print("✗ Could not extract video info")
    
    # Test basic operations
    test_basic_ffmpeg_operations(video_path)
    
    # Test loop operations
    test_loop_operations(video_path)
    
    print("\n" + "=" * 40)
    print("Debug complete!")

if __name__ == "__main__":
    main()
