import os
import re
import subprocess
import sys
import time
import random

def random_wait():
    """Pauses the script for a random duration between 5 and 10 seconds."""
    # random.uniform generates a random decimal (e.g., 7.42), which makes it look more human
    wait_time = random.uniform(5, 10) 
    print(f"Waiting for {wait_time:.2f} seconds...")
    time.sleep(wait_time)


def get_installed_chrome_major_version():
    """Dynamically detects the installed Chrome browser's major version across Windows, Linux, and macOS."""
    version_str = None
    try:
        if sys.platform.startswith("linux"):
            for cmd in ["google-chrome --version", "google-chrome-stable --version", "chromium --version", "chromium-browser --version"]:
                try:
                    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
                    version_str = out
                    break
                except Exception:
                    pass
        elif sys.platform == "win32":
            reg_cmds = [
                'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version',
                'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome" /v DisplayVersion',
                'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome" /v DisplayVersion'
            ]
            for cmd in reg_cmds:
                try:
                    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
                    version_str = out
                    break
                except Exception:
                    pass
        elif sys.platform == "darwin":
            cmd = "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version"
            try:
                version_str = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
            except Exception:
                pass
    except Exception:
        pass

    if version_str:
        match = re.search(r'(\d+)\.\d+\.\d+\.\d+', version_str)
        if match:
            return int(match.group(1))

    return None