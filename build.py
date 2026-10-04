#!/usr/bin/env python3
"""
Production Build Script for SAP Automation Suite GUI.
Creates a standalone executable using PyInstaller with all required hidden imports,
data dependencies, and third-party package hooks (undetected_chromedriver, selenium, pandas, openpyxl).
"""

import os
import shutil
import sys
import subprocess

APP_VERSION = "2.2.0"

def run_build():
    print("==================================================")
    print(f"  SAP Automation Suite v{APP_VERSION} — Build Engine ")
    print("==================================================")

    # 1. Ensure PyInstaller is installed
    try:
        import PyInstaller.__main__
    except ImportError:
        print("[ERROR] PyInstaller is not installed. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller.__main__

    # 2. Clean previous build artifacts
    cwd = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(cwd, "dist")
    build_dir = os.path.join(cwd, "build")
    spec_file = os.path.join(cwd, f"SAP_Automation_Suite_v{APP_VERSION}.spec")
    old_spec = os.path.join(cwd, "SAP_Automation_Suite.spec")

    for path in [dist_dir, build_dir, spec_file, old_spec]:
        if os.path.isdir(path):
            print(f"[CLEAN] Removing old directory: {path}")
            shutil.rmtree(path)
        elif os.path.isfile(path):
            print(f"[CLEAN] Removing old file: {path}")
            os.remove(path)

    # 3. Target configuration
    entry_script = os.path.join(cwd, "gui.py")
    app_name = f"SAP_Automation_Suite_v{APP_VERSION}"

    # Build PyInstaller arguments list
    pyinstaller_args = [
        entry_script,
        f"--name={app_name}",
        "--onefile",             # Create a single standalone executable binary
        "--noconfirm",           # Replace existing spec/dist without asking
        "--clean",               # Clean PyInstaller cache before building
        "--windowed",            # GUI app (no background terminal window popup)
        f"--paths={cwd}",        # Ensure local modules (test1, send_message, etc.) are in Python path

        # Collect full package contents (hooks, submodules, binaries, data)
        "--collect-all=undetected_chromedriver",
        "--collect-all=selenium",
        "--collect-all=pandas",
        "--collect-all=openpyxl",

        # Exclude heavy unused packages
        "--exclude-module=pytest",
        "--exclude-module=scipy",
        "--exclude-module=matplotlib",

        # Explicit Hidden Imports (Local and Third-Party)
        "--hidden-import=test1",
        "--hidden-import=send_message",
        "--hidden-import=enter_details",
        "--hidden-import=helper_utils",
        "--hidden-import=undetected_chromedriver",
        "--hidden-import=undetected_chromedriver.patcher",
        "--hidden-import=selenium",
        "--hidden-import=selenium.webdriver",
        "--hidden-import=selenium.webdriver.common.by",
        "--hidden-import=selenium.webdriver.support.expected_conditions",
        "--hidden-import=selenium.webdriver.support.ui",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.scrolledtext",
    ]

    # Add config file if exists
    config_file = os.path.join(cwd, "gui_settings.json")
    if os.path.exists(config_file):
        sep = ";" if sys.platform == "win32" else ":"
        pyinstaller_args.append(f"--add-data={config_file}{sep}.")

    print(f"\n[BUILD] Launching PyInstaller for script: {entry_script}")
    print(f"[BUILD] Output executable name: {app_name}")

    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n==================================================")
        print("  BUILD SUCCESSFUL!")
        print(f"  Executable created at: {os.path.join(dist_dir, app_name)}")
        print("==================================================")
    except Exception as e:
        print(f"\n[FATAL BUILD ERROR]: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_build()
