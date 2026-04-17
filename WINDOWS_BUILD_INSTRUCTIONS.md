# CAD Automation Windows Compilation Guide

This guide explains how to bundle the `CAD-Automation` Python project into a standalone Windows executable (`.exe`) that includes the GUI, the Cad parser, and all required images and icons.

## Prerequisites (Windows Machine)

1. **Install Python**: You must have Python (preferably 3.10 or newer) installed on your Windows machine.
2. **Clone the Repository**:
   Open a terminal (Command Prompt or PowerShell) and clone the `main` branch which has all the latest fixes and PyInstaller prep code:
   ```cmd
   git clone https://github.com/rhassan9/CAD-Automation.git
   cd CAD-Automation
   ```

## Step 1: Install Required Libraries
You need to install the dependencies required by the application as well as PyInstaller itself.
Run this inside your `CAD-Automation` directory:
```cmd
pip install ezdxf openpyxl customtkinter pillow pyinstaller
```

## Step 2: Build the `.exe` File
PyInstaller needs specific flags to properly package your interface images (`Materials` folder).

Run the following command exactly as written:
```cmd
pyinstaller --noconfirm --onedir --windowed --icon "Materials/App Icon.ico" --name "CAD Extraction Engine" --add-data "Materials/;Materials/" "main.py"
```

### Understanding the Flags:
- `--onedir`: Creates a highly stable folder containing your app and dependencies (much faster and more reliable than `--onefile` for apps with heavy UI images).
- `--windowed`: Prevents the black command prompt/terminal window from popping up behind your UI when users double click it.
- `--icon`: Injects your custom icon into the actual `.exe` file.
- `--add-data "Materials/;Materials/"`: Tells PyInstaller to embed your background and logo pictures into the final build.

## Step 3: Run Your App
Once the bundling completes successfully:
1. Go into the newly created `dist/` folder.
2. Open the `CAD Extraction Engine/` folder.
3. Your application is the `CAD Extraction Engine.exe` file inside.

You can now zip the entire `CAD Extraction Engine` folder and send it to your client!
