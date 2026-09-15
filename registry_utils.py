"""Utilidades de bajo nivel para leer y escribir el Registro de Windows.

Todo el acceso usa la vista de 64 bits (KEY_WOW64_64KEY) para que las claves
sean coherentes con las que ve el Editor del Registro en Windows 11.
"""
import ctypes
import winreg

# Mapa de raíces abreviadas -> handle real de winreg
ROOTS = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKU": winreg.HKEY_USERS,
}

# Centinelas usados en el catálogo de ajustes
DELETE = "__DELETE__"   # borrar el valor / la clave para restaurar el predeterminado
KEY = "__KEY__"         # crear la clave (para ajustes basados en existencia de clave)

_READ = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
_WRITE = winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY


def is_admin() -> bool:
    """Devuelve True si el proceso actual tiene privilegios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def read_value(root: str, path: str, name: str):
    """Lee un valor del registro. Devuelve None si la clave o el valor no existen."""
    try:
        key = winreg.OpenKey(ROOTS[root], path, 0, _READ)
    except FileNotFoundError:
        return None
    except OSError:
        return None
    try:
        value, _ = winreg.QueryValueEx(key, name)
        return value
    except FileNotFoundError:
        return None
    finally:
        winreg.CloseKey(key)


def key_exists(root: str, path: str) -> bool:
    """True si la clave del registro existe."""
    try:
        key = winreg.OpenKey(ROOTS[root], path, 0, _READ)
        winreg.CloseKey(key)
        return True
    except (FileNotFoundError, OSError):
        return False


def set_value(root: str, path: str, name: str, reg_type: int, value) -> None:
    """Crea la clave si hace falta y escribe el valor indicado."""
    key = winreg.CreateKeyEx(ROOTS[root], path, 0, _WRITE)
    try:
        winreg.SetValueEx(key, name, 0, reg_type, value)
    finally:
        winreg.CloseKey(key)


def delete_value(root: str, path: str, name: str) -> None:
    """Borra un valor; ignora si ya no existe."""
    try:
        key = winreg.OpenKey(ROOTS[root], path, 0, _WRITE)
    except (FileNotFoundError, OSError):
        return
    try:
        winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass
    finally:
        winreg.CloseKey(key)


def create_key_with_default(root: str, path: str) -> None:
    """Crea una clave con su valor predeterminado vacío (REG_SZ)."""
    key = winreg.CreateKeyEx(ROOTS[root], path, 0, _WRITE)
    try:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
    finally:
        winreg.CloseKey(key)


def delete_key_tree(root: str, path: str) -> None:
    """Borra una clave y todas sus subclaves de forma recursiva.

    Si una subclave no se puede eliminar (bloqueada por otro proceso, permisos
    insuficientes, etc.), EnumKey(key, 0) seguiría devolviendo siempre el mismo
    nombre. Se detecta ese estancamiento para no entrar en un bucle infinito
    que congelaría la aplicación.
    """
    try:
        key = winreg.OpenKey(ROOTS[root], path, 0, winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY)
    except (FileNotFoundError, OSError):
        return
    try:
        last_stuck = None
        while True:
            try:
                sub = winreg.EnumKey(key, 0)
            except OSError:
                break
            if sub == last_stuck:
                break   # no se pudo eliminar esta subclave: evitar bucle infinito
            delete_key_tree(root, path + "\\" + sub)
            last_stuck = sub
    finally:
        winreg.CloseKey(key)
    try:
        winreg.DeleteKeyEx(ROOTS[root], path, winreg.KEY_WOW64_64KEY, 0)
    except (FileNotFoundError, OSError):
        pass
