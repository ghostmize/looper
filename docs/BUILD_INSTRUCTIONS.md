# 🚀 Building Looper v0.9 Portable Executable

This guide explains how to create a single, portable `.exe` file for Looper that can run on any Windows computer without requiring Python installation.

## 📋 Prerequisites

- **Python 3.7+** installed on your system
- **FFmpeg** installed and accessible via PATH
- All dependencies from `requirements.txt` installed

## 🔧 Quick Build (Recommended)

### Option 1: Use the Batch File (Easiest)
1. Double-click `build_looper_exe.bat`
2. Wait for the build process to complete
3. Find your executable in the `dist/` folder

### Option 2: Use Python Script
```bash
python build_exe.py
```

## 📦 Manual Build Process

If you prefer to build manually or customize the process:

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Install Build Requirements
```bash
pip install -r requirements_build.txt
```

### 3. Build the Executable
```bash
pyinstaller --onefile --windowed --name "Looper_v0.9_by_Ghosteam" looper.py
```

## 🎯 Build Output

After successful build, you'll find:
- **`dist/Looper_v0.9_by_Ghosteam.exe`** - Your portable executable (~50-80MB)
- **`build/`** - Temporary build files (can be deleted)
- **`looper.spec`** - PyInstaller specification file (can be deleted)

## 📁 Distribution

The generated `.exe` file is completely portable:
- ✅ **No Python installation required** on target machines
- ✅ **No additional dependencies needed**
- ✅ **Single file distribution**
- ✅ **Works on Windows 7, 8, 10, 11**

**Note:** FFmpeg still needs to be installed on the target machine for video processing.

## 🔧 Customization Options

### Adding an Icon
1. Create or obtain a `.ico` file
2. Edit `build_exe.py` and update the `icon=None` line:
   ```python
   icon='path/to/your/icon.ico'
   ```

### Reducing File Size
1. Install UPX compressor: https://upx.github.io/
2. Add UPX to your system PATH
3. The build script will automatically use UPX if available

### Debug Mode
To create a console version for debugging:
1. Edit `build_exe.py`
2. Change `console=False` to `console=True`

## 🐛 Troubleshooting

### Build Fails with Import Errors
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements_build.txt
```

### Executable is Too Large
- Install UPX compressor for automatic compression
- Remove unused imports from `looper.py`
- Use `--exclude-module` flags for unnecessary packages

### Antivirus False Positives
- Some antivirus software may flag PyInstaller executables
- Add the `dist/` folder to antivirus exclusions during build
- **Code signing is the best solution** - see `CODE_SIGNING_GUIDE.md` for details
- Use `build_exe_with_signing.py` for code-signed builds

## 📊 Expected Results

| Build Type | File Size | Build Time | Features |
|------------|-----------|------------|----------|
| Standard | ~60MB | 2-3 min | Full functionality |
| UPX Compressed | ~25MB | 3-4 min | Full functionality, smaller |
| Debug | ~65MB | 2-3 min | Console output for debugging |

## 🎉 Success!

Once built successfully, you can:
1. Copy the `.exe` file to any Windows computer
2. Run it directly without installation
3. Distribute it to users who don't have Python
4. Use it on systems where you can't install software

The executable includes all Python dependencies and the Looper application in a single file!

---

**Looper v0.9 by Ghosteam** - Perfect Video Loops Made Simple

