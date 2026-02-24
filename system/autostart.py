from __future__ import annotations

import platform
from pathlib import Path


def ensure_windows_startup(app_name: str, command: str) -> str:
    """Configure startup entry on Windows via HKCU Run."""
    if platform.system().lower() != "windows":
        return "Autostart ignorado: sistema atual não é Windows."

    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)

    return f"Autostart configurado para {app_name}: {command}"


def startup_command_from_main(main_file: str = "main.py") -> str:
    file_path = Path(main_file).resolve()
    return f'python "{file_path}"'
