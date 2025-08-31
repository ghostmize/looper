#!/usr/bin/env python3
"""
FFmpeg Test Script for Looper
Tests FFmpeg functionality and common operations
"""

import subprocess
import sys
import os

def test_ffmpeg_installation():
    """Test if FFmpeg is properly installed"""
    print("Testing FFmpeg installation...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ FFmpeg is installed and working")
            # Print version info
            version_line = result.stdout.split('\n')[0]
            print(f"  Version: {version_line}")
            return True
        else:
            print("✗ FFmpeg returned error code:", result.returncode)
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("✗ FFmpeg command timed out")
        return False

def test_ffmpeg_codecs():
    """Test if required codecs are available"""
    print("\nTesting required codecs...")
    
    # Test HAP codec
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                               '-c:v', 'hap', '-y', 'test_hap.mov'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ HAP codec is available")
            os.remove('test_hap.mov')  # Clean up
        else:
            print("✗ HAP codec not available")
            print("  Error:", result.stderr)
    except Exception as e:
        print("✗ Error testing HAP codec:", e)
    
    # Test H.264 codec
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                               '-c:v', 'libx264', '-y', 'test_mp4.mp4'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ H.264 codec is available")
            os.remove('test_mp4.mp4')  # Clean up
        else:
            print("✗ H.264 codec not available")
            print("  Error:", result.stderr)
    except Exception as e:
        print("✗ Error testing H.264 codec:", e)

def test_filter_complex():
    """Test filter complex functionality"""
    print("\nTesting filter complex...")
    try:
        # Test a simple filter complex
        filter_str = "[0:v]trim=0:1,setpts=PTS-STARTPTS[outv]"
        result = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=2:size=320x240:rate=1', 
                               '-filter_complex', filter_str, '-map', '[outv]', '-c:v', 'libx264', '-y', 'test_filter.mp4'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Filter complex is working")
            os.remove('test_filter.mp4')  # Clean up
        else:
            print("✗ Filter complex failed")
            print("  Error:", result.stderr)
    except Exception as e:
        print("✗ Error testing filter complex:", e)

def test_xfade():
    """Test xfade filter"""
    print("\nTesting xfade filter...")
    try:
        # Create two test videos
        subprocess.run(['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                       '-c:v', 'libx264', '-y', 'test1.mp4'], 
                      capture_output=True, text=True, timeout=30)
        subprocess.run(['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                       '-c:v', 'libx264', '-y', 'test2.mp4'], 
                      capture_output=True, text=True, timeout=30)
        
        # Test xfade
        filter_str = "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=0.5[outv]"
        result = subprocess.run(['ffmpeg', '-hide_banner', '-i', 'test1.mp4', '-i', 'test2.mp4', 
                               '-filter_complex', filter_str, '-map', '[outv]', '-c:v', 'libx264', '-y', 'test_xfade.mp4'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Xfade filter is working")
            # Clean up
            for file in ['test1.mp4', 'test2.mp4', 'test_xfade.mp4']:
                if os.path.exists(file):
                    os.remove(file)
        else:
            print("✗ Xfade filter failed")
            print("  Error:", result.stderr)
    except Exception as e:
        print("✗ Error testing xfade:", e)

def main():
    print("FFmpeg Test Suite for Looper")
    print("=" * 40)
    
    # Test basic installation
    if not test_ffmpeg_installation():
        print("\n❌ FFmpeg installation test failed!")
        print("Please install FFmpeg and add it to your PATH")
        return False
    
    # Test codecs
    test_ffmpeg_codecs()
    
    # Test filter complex
    test_filter_complex()
    
    # Test xfade
    test_xfade()
    
    print("\n✅ FFmpeg test suite completed!")
    print("If all tests passed, FFmpeg should work with Looper.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

