"""Recopila información del equipo (CPU, RAM, GPU, discos, Windows) sin
dependencias externas nuevas: usa ctypes (APIs de Windows) y el Registro.

Solo el tipo de disco (SSD/HDD) usa PowerShell/CIM en segundo plano, porque
no existe una ruta de registro fiable para eso; el resto es instantáneo.
"""
import ctypes
import json
import os
import subprocess

from registry_utils import read_value

_NOWINDOW = 0x08000000


def _run_ps(cmd, timeout=8):
    """Ejecuta un comando de PowerShell y devuelve su salida (vacía si falla)."""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
            creationflags=_NOWINDOW)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def windows_version():
    """Edición, versión (24H2...) y número de build de Windows."""
    path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    product = read_value("HKLM", path, "ProductName") or "Windows"
    display = read_value("HKLM", path, "DisplayVersion") or ""
    build = read_value("HKLM", path, "CurrentBuildNumber") or ""
    ubr = read_value("HKLM", path, "UBR")
    build_full = f"{build}.{ubr}" if (build and ubr is not None) else str(build)
    arch = "64 bits" if ctypes.sizeof(ctypes.c_void_p) == 8 else "32 bits"
    return {"product": str(product), "display_version": str(display),
            "build": build_full, "arch": arch}


def cpu_info():
    """Nombre del procesador (registro, instantáneo) y número de hilos."""
    name = read_value(
        "HKLM", r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        "ProcessorNameString")
    name = (name or "Procesador desconocido").strip()
    name = " ".join(name.split())   # colapsa espacios dobles frecuentes en este valor
    return {"name": name, "threads": os.cpu_count() or 1}


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def ram_info():
    """RAM total/usada en GB, vía la API de Windows (sin subprocess)."""
    try:
        stat = _MemoryStatusEx()
        stat.dwLength = ctypes.sizeof(_MemoryStatusEx)
        ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        if not ok:
            raise OSError("GlobalMemoryStatusEx falló")
        total_gb = stat.ullTotalPhys / (1024 ** 3)
        avail_gb = stat.ullAvailPhys / (1024 ** 3)
        return {"total_gb": total_gb, "used_gb": max(0.0, total_gb - avail_gb),
                "percent": stat.dwMemoryLoad}
    except Exception:
        return {"total_gb": 0.0, "used_gb": 0.0, "percent": 0}


def gpu_info():
    """Tarjetas gráficas instaladas, leyendo la clase 'Display adapters'
    del registro (sin WMI/PowerShell): una subclave numerada por adaptador."""
    base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    gpus = []
    misses = 0
    for i in range(16):
        sub = f"{base}\\{i:04d}"
        name = read_value("HKLM", sub, "DriverDesc")
        if name is None:
            misses += 1
            if misses > 2:      # un par de huecos es normal; más, se acabaron los adaptadores
                break
            continue
        vram = read_value("HKLM", sub, "HardwareInformation.qwMemorySize")
        if not isinstance(vram, int) or vram <= 0:
            vram = read_value("HKLM", sub, "HardwareInformation.MemorySize")
        vram_gb = round(vram / (1024 ** 3), 1) if isinstance(vram, int) and vram > 0 else None
        gpus.append({"name": str(name).strip(), "vram_gb": vram_gb})
    return gpus or [{"name": "No detectada", "vram_gb": None}]


def disks_info():
    """Espacio total/libre de cada unidad de disco fija (sin subprocess)."""
    disks = []
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    except Exception:
        return disks
    for i in range(26):
        if not (bitmask >> i) & 1:
            continue
        letter = f"{chr(65 + i)}:\\"
        try:
            if ctypes.windll.kernel32.GetDriveTypeW(letter) != 3:   # 3 = DRIVE_FIXED
                continue
            free_avail = ctypes.c_ulonglong(0)
            total = ctypes.c_ulonglong(0)
            total_free = ctypes.c_ulonglong(0)
            ok = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                letter, ctypes.byref(free_avail), ctypes.byref(total), ctypes.byref(total_free))
            if not ok or total.value == 0:
                continue
            total_gb = total.value / (1024 ** 3)
            free_gb = total_free.value / (1024 ** 3)
            disks.append({"letter": letter, "total_gb": total_gb, "free_gb": free_gb,
                          "used_gb": max(0.0, total_gb - free_gb)})
        except Exception:
            continue
    return disks


def disk_media_types():
    """SSD/HDD de cada disco físico. Requiere PowerShell/CIM (no hay ruta de
    registro fiable); se pensó para llamarse en un hilo aparte, ya que puede
    tardar y en algunas ediciones de Windows no está disponible."""
    out = _run_ps("Get-PhysicalDisk | Select-Object FriendlyName,MediaType "
                  "| ConvertTo-Json -Compress")
    if not out:
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        return [{"name": d.get("FriendlyName") or "Disco",
                 "media": d.get("MediaType") or "Desconocido"} for d in data]
    except Exception:
        return []
