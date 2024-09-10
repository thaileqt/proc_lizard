#!/usr/bin/env python
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "packages": ["pygame", "pystray", "win32api", "win32con", "win32gui", "PIL", "psutil"],
    "include_files": [
        ("icon.png", "icon.png"),  # Include your icon file
    ],
}

setup(
    name="lizark",
    version="0.1",
    description="Lizark in your area!",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI")],
)