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

## Step 1: Create a Clean Virtual Environment (Crucial)
To guarantee your `.exe` file is as small and fast as possible without picking up unnecessary global Python packages from your computer, create a fresh sandbox.

Run these inside your `CAD-Automation` directory:
```cmd
python -m venv venv
venv\Scripts\activate
```
*(You will know it worked if you see `(venv)` appear at the start of your command prompt)*

## Step 2: Install Required Libraries
With your virtual environment active, install precisely the dependencies required by the application:
```cmd
pip install ezdxf openpyxl customtkinter pillow pyinstaller
```

## Step 3: Build the `.exe` File
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

## Step 4: Run Your App
Once the bundling completes successfully:
1. Go into the newly created `dist/` folder.
2. Open the `CAD Extraction Engine/` folder.
3. Your application is the `CAD Extraction Engine.exe` file inside.

You can now zip the entire `CAD Extraction Engine` folder and send it to your client!
