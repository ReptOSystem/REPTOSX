"""Programas que se abren al iniciar sesión en Windows.

Se leen las claves Run del Registro y las carpetas de Inicio. Para activar o
desactivar una entrada se usa el mismo mecanismo que el Administrador de
tareas (la clave StartupApproved): no se borra nada, así que el cambio es
reversible y Windows lo muestra igual en su propia pestaña de Inicio.

No se incluyen las apps de la Tienda ni las tareas programadas, que Windows
gestiona por otras vías.
"""
import os
import struct
import time
import winreg

from registry_utils import enum_values, read_value, set_value

_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"
_RUN32 = r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
_APPROVED = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved"
_STARTUP_DIR = r"Microsoft\Windows\Start Menu\Programs\Startup"

# (raíz, clave Run, subclave de StartupApproved)
_REG_SOURCES = [
    ("HKCU", _RUN, "Run"),
    ("HKLM", _RUN, "Run"),
    ("HKLM", _RUN32, "Run32"),
]


def _folders():
    """(raíz de StartupApproved, carpeta) de las carpetas de Inicio."""
    result = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        result.append(("HKCU", os.path.join(appdata, _STARTUP_DIR)))
    programdata = os.environ.get("PROGRAMDATA")
    if programdata:
        result.append(("HKLM", os.path.join(programdata, _STARTUP_DIR)))
    return result


def is_enabled(item) -> bool:
    """Sin marca en StartupApproved, la entrada está activa. Si la hay, el
    primer byte es par (02, 06) cuando está activa e impar (03, 07) cuando no."""
    data = read_value(item["root"], _APPROVED + "\\" + item["approved"], item["key"])
    if not isinstance(data, bytes) or not data:
        return True
    return data[0] % 2 == 0


def set_enabled(item, enabled: bool) -> None:
    if enabled:
        data = b"\x02" + b"\x00" * 11
    else:
        # 03 + fecha (FILETIME) en la que se desactivó, como hace Windows
        filetime = int((time.time() + 11644473600) * 10_000_000)
        data = b"\x03\x00\x00\x00" + struct.pack("<Q", filetime)
    set_value(item["root"], _APPROVED + "\\" + item["approved"], item["key"],
              winreg.REG_BINARY, data)


def list_items():
    """Lista de entradas de inicio: name, command, source ('user' | 'machine'
    | 'folder'), admin (hace falta administrador para cambiarla) y enabled."""
    items = []
    for root, run_path, approved in _REG_SOURCES:
        for name, value, _type in enum_values(root, run_path):
            if not name or not isinstance(value, str) or not value.strip():
                continue
            items.append({"name": name, "command": value.strip(), "key": name,
                          "root": root, "approved": approved,
                          "source": "user" if root == "HKCU" else "machine",
                          "admin": root == "HKLM"})
    for root, folder in _folders():
        try:
            files = os.listdir(folder)
        except OSError:
            continue
        for fname in files:
            if fname.lower() == "desktop.ini":
                continue
            items.append({"name": os.path.splitext(fname)[0],
                          "command": os.path.join(folder, fname), "key": fname,
                          "root": root, "approved": "StartupFolder",
                          "source": "folder", "admin": root == "HKLM"})
    for item in items:
        item["enabled"] = is_enabled(item)
    items.sort(key=lambda it: it["name"].lower())
    return items
