# -*- coding: utf-8 -*-
"""
Desktop Pet Packaging Tool
Builds a standalone executable for macOS (.app) or Windows (.exe) using PyInstaller.
"""

import os
import sys
import subprocess


def build():
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller is not installed.")
        print("[*] Please run: pip install pyinstaller")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sep = ";" if sys.platform.startswith("win") else ":"
    assets_data = f"assets{sep}assets"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--clean",
        "--name=DesktopPet",
        f"--add-data={assets_data}",
        os.path.join(base_dir, "main.py"),
    ]

    print("[*] Building standalone Desktop Pet application...")
    print("[*] Command:", " ".join(cmd))
    ret = subprocess.call(cmd, cwd=base_dir)
    if ret == 0:
        print("\n[+] Build succeeded!")
        print(f"[+] Executable output directory: {os.path.join(base_dir, 'dist')}")
    else:
        print(f"\n[-] Build failed with exit code: {ret}")


if __name__ == "__main__":
    build()
