"""Catálogo de ajustes del Registro para personalizar y optimizar Windows 11.

Cada ajuste (Tweak) describe uno o varios valores del registro. El interruptor
de la interfaz representa la ACCIÓN descrita por el nombre del ajuste:
    - Interruptor ACTIVADO    -> se aplica el valor `on`
    - Interruptor DESACTIVADO -> se aplica el valor `off` (a menudo el predeterminado)

Los ajustes se dividen en dos grupos: "Personalización" y "Optimización".

Campo `restart`:
    None        -> el cambio es inmediato
    "explorer"  -> requiere reiniciar el Explorador (botón en la app)
    "pc"        -> requiere reiniciar el PC

Tipos de entrada:
    - Valor normal: name = "NombreValor", on/off = valor a escribir (o DELETE).
    - Existencia de clave: name = None, on = KEY (crear), off = DELETE (borrar árbol).
"""
import subprocess
import winreg

import i18n
from registry_utils import DELETE, KEY, key_exists, read_value, \
    set_value, delete_value, create_key_with_default, delete_key_tree

DWORD = winreg.REG_DWORD
SZ = winreg.REG_SZ
BIN = winreg.REG_BINARY

GROUPS = ["personalization", "optimization"]

# Ejecuta un comando sin abrir ventana de consola
_NOWINDOW = 0x08000000


def _run(args, timeout=10):
    # timeout defensivo: evita que un comando externo colgado (p.ej. una base
    # de planes de energía corrupta) congele la interfaz indefinidamente
    return subprocess.run(args, capture_output=True, text=True,
                          creationflags=_NOWINDOW, timeout=timeout)


# --- Plan de energía (powercfg, no es registro) ---
_HIGH_PERF = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
_BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"


def _power_is_high():
    # Nota: usar el guion ('-'), no la barra ('/'): en algunas configuraciones
    # regionales 'powercfg /getactivescheme' devuelve "Parámetros no válidos".
    try:
        return _HIGH_PERF in _run(["powercfg", "-getactivescheme"]).stdout.lower()
    except Exception:
        return False


def _power_set(turn_on):
    guid = _HIGH_PERF if turn_on else _BALANCED
    try:
        r = _run(["powercfg", "-setactive", guid])
        if turn_on and r.returncode != 0:
            # el plan podría estar oculto: lo duplicamos y activamos
            _run(["powercfg", "-duplicatescheme", _HIGH_PERF])
            _run(["powercfg", "-setactive", _HIGH_PERF])
    except Exception:
        pass   # se ignora: is_on() reflejará el plan realmente activo tras el intento


# --- Algoritmo de Nagle (por adaptador de red, no es una ruta fija) ---
def _tcpip_interfaces():
    """Enumera las subclaves de interfaces de red (una por adaptador) bajo
    Tcpip\\Parameters\\Interfaces. No hay una ruta fija: cada adaptador tiene
    su propio GUID, así que hay que descubrirlas dinámicamente."""
    base = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    ifaces = []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base, 0,
                             winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
    except OSError:
        return ifaces
    try:
        i = 0
        while True:
            try:
                sub = winreg.EnumKey(key, i)
            except OSError:
                break
            ifaces.append(base + "\\" + sub)
            i += 1
    finally:
        winreg.CloseKey(key)
    return ifaces


def _nagle_is_on():
    try:
        ifaces = _tcpip_interfaces()
        if not ifaces:
            return False
        return all(
            read_value("HKLM", p, "TcpAckFrequency") == 1
            and read_value("HKLM", p, "TCPNoDelay") == 1
            for p in ifaces)
    except Exception:
        return False


def _nagle_set(turn_on):
    try:
        for path in _tcpip_interfaces():
            if turn_on:
                set_value("HKLM", path, "TcpAckFrequency", DWORD, 1)
                set_value("HKLM", path, "TCPNoDelay", DWORD, 1)
            else:
                delete_value("HKLM", path, "TcpAckFrequency")
                delete_value("HKLM", path, "TCPNoDelay")
    except Exception:
        pass


def E(root, path, name, on, off, rtype=DWORD):
    """Crea la descripción de una entrada de registro."""
    return {"root": root, "path": path, "name": name,
            "on": on, "off": off, "type": rtype}


class Tweak:
    def __init__(self, id, group, category, name, desc, entries,
                 admin=False, restart=None, cleanup_keys=None,
                 is_on_fn=None, apply_fn=None, danger=False):
        self.id = id
        self.group = group             # clave interna: "personalization" | "optimization"
        self.category = category       # clave interna: "appearance", "taskbar", etc.
        self._name_es = name
        self._desc_es = desc
        self.entries = entries
        self.admin = admin            # requiere privilegios de administrador
        self.restart = restart        # None | "explorer" | "pc"
        self.danger = danger          # reduce la seguridad: pedir confirmación
        # claves a borrar por completo al desactivar (menús contextuales, etc.)
        self.cleanup_keys = cleanup_keys or []
        # acciones a medida (ej. powercfg) que sustituyen la lógica de registro
        self.is_on_fn = is_on_fn
        self.apply_fn = apply_fn

    @property
    def name(self) -> str:
        """Nombre en el idioma activo (español por defecto, inglés si i18n.get_lang()=='en')."""
        return i18n.tweak_name(self)

    @property
    def desc(self) -> str:
        """Descripción en el idioma activo."""
        return i18n.tweak_desc(self)

    def is_on(self) -> bool:
        """True solo si TODAS las entradas están en su valor `on`."""
        if self.is_on_fn:
            return bool(self.is_on_fn())
        for e in self.entries:
            if e["name"] is None:
                if not key_exists(e["root"], e["path"]):
                    return False
            else:
                cur = read_value(e["root"], e["path"], e["name"])
                if cur != e["on"]:
                    return False
        return True

    def apply(self, turn_on: bool) -> None:
        if self.apply_fn:
            self.apply_fn(turn_on)
            return
        if not turn_on and self.cleanup_keys:
            # al desactivar, borrar las claves completas (no valor por valor)
            for root, path in self.cleanup_keys:
                delete_key_tree(root, path)
            return
        for e in self.entries:
            target = e["on"] if turn_on else e["off"]
            if e["name"] is None:
                if target == KEY:
                    create_key_with_default(e["root"], e["path"])
                elif target == DELETE:
                    delete_key_tree(e["root"], e["path"])
                continue
            if target == DELETE:
                delete_value(e["root"], e["path"], e["name"])
            else:
                set_value(e["root"], e["path"], e["name"], e["type"], target)


# Rutas reutilizadas
ADV = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
EXPL = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
PERS = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
CDM = r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
SEARCH = r"Software\Microsoft\Windows\CurrentVersion\Search"
NEWSTART = EXPL + r"\HideDesktopIcons\NewStartPanel"
DESKTOP = r"Control Panel\Desktop"

P = "personalization"
O = "optimization"


TWEAKS = [
    # =======================================================================
    # ============================ PERSONALIZACIÓN ==========================
    # =======================================================================

    # ----------------------------- Apariencia ------------------------------
    Tweak("dark_apps", P, "appearance", "Modo oscuro en aplicaciones",
          "Pone en tema oscuro las aplicaciones modernas (Configuración, Explorador, Tienda...). "
          "No afecta a la barra de tareas ni al menú Inicio (eso es el modo oscuro del sistema).",
          [E("HKCU", PERS, "AppsUseLightTheme", 0, 1)], restart="explorer"),
    Tweak("dark_system", P, "appearance", "Modo oscuro en el sistema",
          "Pone en tema oscuro la barra de tareas, el menú Inicio, el centro de notificaciones "
          "y los menús del sistema.",
          [E("HKCU", PERS, "SystemUsesLightTheme", 0, 1)], restart="explorer"),
    Tweak("wallpaper_quality", P, "appearance", "Máxima calidad del fondo de pantalla",
          "Hace que Windows aplique el fondo de escritorio sin recomprimirlo a JPEG (calidad 100%), "
          "evitando pérdida de nitidez. Vuelve a establecer el fondo después de activarlo.",
          [E("HKCU", DESKTOP, "JPEGImportQuality", 100, DELETE)]),
    Tweak("disable_shake", P, "appearance", "Desactivar 'sacudir para minimizar' (Aero Shake)",
          "Al agarrar y sacudir una ventana, Windows ya no minimizará todas las demás "
          "(evita minimizar todo sin querer al mover ventanas).",
          [E("HKCU", ADV, "DisallowShaking", 1, 0)]),

    # --------------------------- Barra de tareas ---------------------------
    Tweak("taskbar_left", P, "taskbar", "Alinear la barra de tareas a la izquierda",
          "Alinea los iconos y el botón Inicio a la izquierda de la barra de tareas, "
          "como en Windows 10, en lugar de centrados.",
          [E("HKCU", ADV, "TaskbarAl", 0, 1)], restart="explorer"),
    Tweak("hide_taskview", P, "taskbar", "Ocultar el botón Vista de tareas",
          "Oculta el botón de Vista de tareas (el de los escritorios virtuales) de la barra de tareas. "
          "El atajo Win+Tab sigue funcionando.",
          [E("HKCU", ADV, "ShowTaskViewButton", 0, 1)], restart="explorer"),
    Tweak("hide_search", P, "taskbar", "Ocultar el cuadro de búsqueda",
          "Oculta por completo el cuadro o el icono de búsqueda de la barra de tareas. "
          "Podrás seguir buscando con la tecla Windows.",
          [E("HKCU", SEARCH, "SearchboxTaskbarMode", 0, 3)], restart="explorer"),
    Tweak("never_combine", P, "taskbar", "Nunca combinar botones (mostrar etiquetas)",
          "Cada ventana abierta aparece como un botón independiente con su título, sin agruparse "
          "(modo 'No combinar nunca' de Windows 10). Necesita Windows 11 23H2 o superior.",
          [E("HKCU", ADV, "TaskbarGlomLevel", 2, 0)], restart="explorer"),
    Tweak("tray_show_all", P, "taskbar", "Mostrar todos los iconos de la bandeja",
          "Muestra siempre todos los iconos del área de notificación (junto al reloj), sin esconderlos "
          "en el menú de desbordamiento (la flechita).",
          [E("HKCU", EXPL, "EnableAutoTray", 0, 1)], restart="explorer"),
    Tweak("end_task", P, "taskbar", "Añadir 'Finalizar tarea' al clic derecho",
          "Añade la opción 'Finalizar tarea' al menú del clic derecho sobre cualquier app de la barra "
          "de tareas, para cerrarla al instante. Necesita Windows 11 23H2 o superior.",
          [E("HKCU", ADV, "TaskbarEndTask", 1, 0)], restart="explorer"),

    # ----------------------------- Menú Inicio -----------------------------
    Tweak("disable_bing", P, "start_menu", "Desactivar la búsqueda web (Bing) en Inicio",
          "Elimina los resultados de internet y de Bing del menú Inicio y del cuadro de búsqueda; "
          "así la búsqueda solo mira en tu equipo y es más rápida.",
          [E("HKCU", SEARCH, "BingSearchEnabled", 0, 1),
           E("HKCU", r"Software\Policies\Microsoft\Windows\Explorer",
             "DisableSearchBoxSuggestions", 1, DELETE)]),
    Tweak("start_more_pins", P, "start_menu", "Diseño del menú Inicio: más anclajes",
          "Cambia el diseño del menú Inicio para mostrar más filas de aplicaciones ancladas "
          "y reducir la sección de 'Recomendado'.",
          [E("HKCU", ADV, "Start_Layout", 1, 0)], restart="explorer"),
    Tweak("start_track_docs", P, "start_menu", "No mostrar elementos abiertos recientemente",
          "Deja de mostrar los archivos abiertos recientemente en el menú Inicio, en las listas de "
          "salto (clic derecho en iconos de la barra) y en el acceso rápido del Explorador.",
          [E("HKCU", ADV, "Start_TrackDocs", 0, 1)], restart="explorer"),
    Tweak("start_account_notif", P, "start_menu", "Desactivar notificaciones de cuenta en Inicio",
          "Quita los avisos y sugerencias sobre tu cuenta de Microsoft que aparecen sobre tu nombre "
          "en el menú Inicio.",
          [E("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Start",
             "Start_AccountNotifications", 0, 1)], restart="explorer"),
    Tweak("disable_copilot", P, "start_menu", "Desactivar Windows Copilot",
          "Desactiva el asistente Windows Copilot mediante directiva: oculta su botón e impide que se abra.",
          [E("HKCU", r"Software\Policies\Microsoft\Windows\WindowsCopilot",
             "TurnOffWindowsCopilot", 1, DELETE)]),

    # ------------------------------ Explorador -----------------------------
    Tweak("show_ext", P, "explorer", "Mostrar extensiones de archivo",
          "Muestra la extensión (.txt, .exe, .jpg...) de todos los archivos. Ayuda a detectar "
          "archivos engañosos como 'foto.jpg.exe'.",
          [E("HKCU", ADV, "HideFileExt", 0, 1)], restart="explorer"),
    Tweak("show_hidden", P, "explorer", "Mostrar archivos ocultos",
          "Muestra los archivos y carpetas marcados con el atributo 'oculto'.",
          [E("HKCU", ADV, "Hidden", 1, 2)], restart="explorer"),
    Tweak("show_super_hidden", P, "explorer", "Mostrar archivos protegidos del sistema",
          "Muestra también los archivos protegidos del sistema operativo (como pagefile.sys). "
          "Úselo con precaución: no borres lo que no conozcas.",
          [E("HKCU", ADV, "ShowSuperHidden", 1, 0)], restart="explorer"),
    Tweak("classic_menu", P, "explorer", "Menú contextual clásico (estilo Windows 10)",
          "Devuelve el menú del clic derecho completo de Windows 10, sin tener que pulsar "
          "'Mostrar más opciones' para ver todo.",
          [E("HKCU", r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32",
             None, KEY, DELETE)], restart="explorer"),
    Tweak("compact_mode", P, "explorer", "Vista compacta en el Explorador",
          "Reduce el espacio entre archivos y carpetas para que quepan más elementos en pantalla "
          "(aspecto más parecido a Windows 10).",
          [E("HKCU", ADV, "UseCompactMode", 1, 0)], restart="explorer"),
    Tweak("launch_thispc", P, "explorer", "Abrir el Explorador en 'Este equipo'",
          "Al abrir el Explorador se muestra 'Este equipo' (las unidades) en lugar de la página "
          "de 'Inicio / Acceso rápido'.",
          [E("HKCU", ADV, "LaunchTo", 1, 2)], restart="explorer"),
    Tweak("nav_expand", P, "explorer", "Expandir a la carpeta actual en el panel",
          "El panel de carpetas de la izquierda se despliega automáticamente hasta la carpeta "
          "que tienes abierta.",
          [E("HKCU", ADV, "NavPaneExpandToCurrentFolder", 1, 0)], restart="explorer"),
    Tweak("drive_letters_first", P, "explorer", "Mostrar la letra de unidad antes del nombre",
          "Muestra las unidades como '(C:) Disco local' en vez de 'Disco local (C:)'.",
          [E("HKCU", EXPL, "ShowDriveLettersFirst", 4, DELETE)], restart="explorer"),
    Tweak("hide_quickaccess", P, "explorer", "Ocultar recientes y frecuentes en el Explorador",
          "Quita la lista de archivos usados recientemente y de carpetas frecuentes de la página "
          "de Inicio del Explorador (más privacidad).",
          [E("HKCU", EXPL, "ShowRecent", 0, 1),
           E("HKCU", EXPL, "ShowFrequent", 0, 1)], restart="explorer"),
    Tweak("remove_shortcut_suffix", P, "explorer", "Quitar el texto '- Acceso directo'",
          "Los accesos directos que crees a partir de ahora ya no añadirán ' - Acceso directo' "
          "al final del nombre.",
          [E("HKCU", EXPL, "link", b"\x00\x00\x00\x00", DELETE, BIN)], restart="explorer"),

    # -------------------------- Escritorio e iconos ------------------------
    Tweak("desktop_thispc", P, "desktop_icons", "Mostrar 'Este equipo' en el escritorio",
          "Añade al escritorio el icono de 'Este equipo' para acceder a las unidades con doble clic.",
          [E("HKCU", NEWSTART, "{20D04FE0-3AEA-1069-A2D8-08002B30309D}", 0, 1)], restart="explorer"),
    Tweak("desktop_userfolder", P, "desktop_icons", "Mostrar la carpeta del usuario",
          "Añade al escritorio el icono de tu carpeta personal (Documentos, Descargas, Imágenes...).",
          [E("HKCU", NEWSTART, "{59031a47-3f72-44a7-89c5-5595fe6b30ee}", 0, 1)], restart="explorer"),
    Tweak("desktop_network", P, "desktop_icons", "Mostrar 'Red' en el escritorio",
          "Añade al escritorio el icono de 'Red' (equipos y recursos compartidos de tu red local).",
          [E("HKCU", NEWSTART, "{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}", 0, 1)], restart="explorer"),
    Tweak("desktop_controlpanel", P, "desktop_icons", "Mostrar 'Panel de control' en el escritorio",
          "Añade al escritorio un acceso directo al Panel de control clásico.",
          [E("HKCU", NEWSTART, "{5399E694-6CE5-4D6C-8FCE-1D8870FDCBA0}", 0, 1)], restart="explorer"),
    Tweak("desktop_hide_recyclebin", P, "desktop_icons", "Ocultar la Papelera de reciclaje",
          "Quita el icono de la Papelera de reciclaje del escritorio (sigues pudiendo vaciarla desde el Explorador).",
          [E("HKCU", NEWSTART, "{645FF040-5081-101B-9F08-00AA002F954E}", 1, 0)], restart="explorer"),

    # -------------------------- Pantalla de bloqueo ------------------------
    Tweak("lockscreen_tips", P, "lock_screen", "Quitar curiosidades y anuncios del bloqueo",
          "Quita los datos curiosos, consejos y anuncios que Windows muestra sobre la imagen "
          "de la pantalla de bloqueo (Windows Spotlight).",
          [E("HKCU", CDM, "RotatingLockScreenOverlayEnabled", 0, 1),
           E("HKCU", CDM, "SubscribedContent-338387Enabled", 0, 1)]),
    Tweak("no_lockscreen", P, "lock_screen", "Desactivar la pantalla de bloqueo",
          "Salta la pantalla de bloqueo (la imagen con el reloj) y va directo a la de inicio de sesión. "
          "Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Personalization",
             "NoLockScreen", 1, DELETE)], admin=True),
    Tweak("logon_blur", P, "lock_screen", "Quitar el desenfoque del inicio de sesión",
          "Elimina el desenfoque (efecto acrylic) del fondo en la pantalla de inicio de sesión, "
          "mostrando la imagen nítida. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",
             "DisableAcrylicBackgroundOnLogon", 1, 0)], admin=True),

    # =======================================================================
    # ============================= OPTIMIZACIÓN ============================
    # =======================================================================

    # ------------------------------ Rendimiento ----------------------------
    Tweak("visual_fx_perf", O, "performance", "Efectos visuales: ajustar para rendimiento",
          "Pone los efectos visuales en 'Ajustar para obtener el mejor rendimiento': desactiva "
          "animaciones, sombras y transparencias de la interfaz. Útil en equipos modestos.",
          [E("HKCU", EXPL + r"\VisualEffects", "VisualFXSetting", 2, 0)], restart="explorer"),
    Tweak("min_animate", O, "performance", "Desactivar animaciones de ventanas",
          "Quita la animación de minimizar y maximizar ventanas; las ventanas aparecen al instante.",
          [E("HKCU", DESKTOP + r"\WindowMetrics", "MinAnimate", "0", "1", SZ)], restart="explorer"),
    Tweak("menu_delay", O, "performance", "Acelerar la apertura de menús",
          "Reduce de 400 ms a 0 ms el retardo con que se abren los menús, haciendo la interfaz "
          "más ágil al pasar el ratón.",
          [E("HKCU", DESKTOP, "MenuShowDelay", "0", "400", SZ)], restart="explorer"),
    Tweak("startup_delay", O, "performance", "Quitar el retardo de inicio de apps",
          "Elimina el retardo artificial (~10 s) que Windows aplica a los programas de inicio, "
          "para que arranquen nada más iniciar sesión.",
          [E("HKCU", EXPL + r"\Serialize", "StartupDelayInMSec", 0, DELETE)]),
    Tweak("mouse_accel", O, "performance", "Desactivar la aceleración del ratón",
          "Desactiva 'mejorar la precisión del puntero', para que el cursor se mueva 1:1 con el ratón "
          "(recomendado para juegos y diseño).",
          [E("HKCU", r"Control Panel\Mouse", "MouseSpeed", "0", "1", SZ),
           E("HKCU", r"Control Panel\Mouse", "MouseThreshold1", "0", "6", SZ),
           E("HKCU", r"Control Panel\Mouse", "MouseThreshold2", "0", "10", SZ)]),
    Tweak("close_hung_apps", O, "performance", "Cerrar apps que no responden más rápido",
          "Reduce los tiempos de espera de Windows antes de forzar el cierre de apps colgadas al "
          "apagar o reiniciar, acelerando el apagado.",
          [E("HKCU", DESKTOP, "AutoEndTasks", "1", "0", SZ),
           E("HKCU", DESKTOP, "HungAppTimeout", "1000", "5000", SZ),
           E("HKCU", DESKTOP, "WaitToKillAppTimeout", "2000", "20000", SZ)], restart="pc"),
    Tweak("foreground_priority", O, "performance", "Priorizar aplicaciones en primer plano",
          "Asigna más tiempo de CPU a la ventana que tienes activa, mejorando su fluidez frente a "
          "las apps en segundo plano. Requiere administrador y reiniciar.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\PriorityControl",
             "Win32PrioritySeparation", 38, 2)], admin=True, restart="pc"),

    # -------------------------- Arranque y apagado -------------------------
    Tweak("disable_fast_startup", O, "boot_shutdown", "Desactivar el inicio rápido",
          "Desactiva el 'Inicio rápido' (una hibernación parcial del sistema). Recomendado si tienes "
          "arranque dual o problemas al apagar/encender. Requiere administrador.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Power",
             "HiberbootEnabled", 0, 1)], admin=True),
    Tweak("disable_hibernation", O, "boot_shutdown", "Desactivar la hibernación",
          "Desactiva la función de hibernar; al hacerlo Windows libera el archivo hiberfil.sys "
          "(varios GB de disco). Requiere administrador y reiniciar.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\Power",
             "HibernateEnabled", 0, 1)], admin=True, restart="pc"),
    Tweak("wait_kill_service", O, "boot_shutdown", "Acelerar el cierre de servicios al apagar",
          "Reduce de 5 s a 2 s el tiempo que Windows espera a cada servicio antes de cerrarlo al "
          "apagar, acortando el apagado. Requiere administrador.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control",
             "WaitToKillServiceTimeout", "2000", "5000", SZ)], admin=True),
    Tweak("startup_sound", O, "boot_shutdown", "Desactivar el sonido de inicio de Windows",
          "Silencia el sonido que reproduce Windows al arrancar e iniciar sesión. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\BootAnimation",
             "DisableStartupSound", 1, 0)], admin=True),
    Tweak("verbose_status", O, "boot_shutdown", "Mensajes de estado detallados",
          "Muestra mensajes detallados ('Iniciando servicios...', etc.) en el arranque y apagado, "
          "en vez de solo 'Bienvenido'. Útil para diagnosticar lentitud. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
             "verbosestatus", 1, 0)], admin=True),

    # ------------------------- Privacidad y telemetría ---------------------
    Tweak("disable_suggested", O, "privacy", "Desactivar contenido sugerido y consejos",
          "Quita las sugerencias de apps, los anuncios y los 'consejos' que Windows muestra en el "
          "menú Inicio, en Configuración y en la línea de tiempo.",
          [E("HKCU", CDM, "SubscribedContent-338393Enabled", 0, 1),
           E("HKCU", CDM, "SubscribedContent-353694Enabled", 0, 1),
           E("HKCU", CDM, "SubscribedContent-353696Enabled", 0, 1),
           E("HKCU", CDM, "SystemPaneSuggestionsEnabled", 0, 1),
           E("HKCU", CDM, "SoftLandingEnabled", 0, 1)]),
    Tweak("stop_app_reinstall", O, "privacy", "Impedir la reinstalación de apps sugeridas",
          "Evita que Windows instale 'por sorpresa' apps promocionadas y bloatware (juegos, TikTok, "
          "etc.) en tu cuenta de forma automática.",
          [E("HKCU", CDM, "SilentInstalledAppsEnabled", 0, 1),
           E("HKCU", CDM, "PreInstalledAppsEnabled", 0, 1),
           E("HKCU", CDM, "OemPreInstalledAppsEnabled", 0, 1)]),
    Tweak("disable_input_personalization", O, "privacy", "Desactivar recopilación de escritura",
          "Impide que Windows recopile y envíe muestras de tu escritura, voz y entintado para "
          "'personalización'.",
          [E("HKCU", r"Software\Microsoft\InputPersonalization", "RestrictImplicitTextCollection", 1, 0),
           E("HKCU", r"Software\Microsoft\InputPersonalization", "RestrictImplicitInkCollection", 1, 0),
           E("HKCU", r"Software\Microsoft\InputPersonalization\TrainedDataStore", "HarvestContacts", 0, 1),
           E("HKCU", r"Software\Microsoft\Personalization\Settings", "AcceptedPrivacyPolicy", 0, 1)]),
    Tweak("disable_feedback", O, "privacy", "Desactivar solicitudes de comentarios",
          "Windows deja de mostrarte periódicamente las ventanas que piden tu opinión (Feedback Hub).",
          [E("HKCU", r"Software\Microsoft\Siuf\Rules", "NumberOfSIUFInPeriod", 0, DELETE)]),
    Tweak("disable_scoobe", O, "privacy", "Quitar 'Terminemos de configurar el dispositivo'",
          "Desactiva la pantalla completa que, tras actualizar, te insiste en configurar "
          "OneDrive, Microsoft 365, etc.",
          [E("HKCU", r"Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement",
             "ScoobeSystemSettingEnabled", 0, 1)]),
    Tweak("disable_telemetry", O, "privacy", "Reducir la telemetría al mínimo",
          "Establece los datos de diagnóstico que se envían a Microsoft en el nivel más bajo posible "
          "(en Home/Pro el mínimo es 'Requerido/Básico'). Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
             "AllowTelemetry", 0, DELETE)], admin=True),
    Tweak("disable_recall", O, "privacy", "Desactivar Windows Recall (IA)",
          "Bloquea por directiva Windows Recall, la función de los equipos Copilot+ que captura "
          "automáticamente imágenes de tu pantalla para analizarlas con IA. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI",
             "DisableAIDataAnalysis", 1, DELETE),
           E("HKCU", r"Software\Policies\Microsoft\Windows\WindowsAI",
             "DisableAIDataAnalysis", 1, DELETE)], admin=True),
    Tweak("disable_websearch", O, "privacy", "Quitar resultados web de la búsqueda",
          "Elimina los resultados de internet del cuadro de búsqueda de Windows; solo busca en tu "
          "equipo, sin enviar lo que escribes. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "DisableWebSearch", 1, 0),
           E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "ConnectedSearchUseWeb", 0, 1)],
          admin=True),

    # --------------------------------- Red ---------------------------------
    Tweak("qos_bandwidth", O, "network", "Liberar el ancho de banda reservado (QoS)",
          "Permite usar el 20% de ancho de banda que Windows reserva por defecto para QoS, dejando "
          "el 100% disponible para tus descargas. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Psched",
             "NonBestEffortLimit", 0, DELETE)], admin=True),
    Tweak("disable_delivery_opt", O, "network", "Desactivar descargas P2P de actualizaciones",
          "Desactiva la Optimización de entrega: tu PC deja de compartir (subir) actualizaciones de "
          "Windows a otros equipos por internet. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization",
             "DODownloadMode", 0, DELETE)], admin=True),

    # ------------------------------- Juegos --------------------------------
    Tweak("disable_game_dvr", O, "gaming", "Desactivar la grabación en segundo plano (Game DVR)",
          "Desactiva la captura/grabación en segundo plano de la Xbox Game Bar, que consume CPU y GPU "
          "mientras juegas. Ganas algo de FPS.",
          [E("HKCU", r"System\GameConfigStore", "GameDVR_Enabled", 0, 1),
           E("HKCU", r"Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0, 1)]),
    Tweak("hags", O, "gaming", "Planificación de GPU por hardware (HAGS)",
          "Activa la 'planificación de GPU acelerada por hardware': deja que la GPU gestione su propia "
          "memoria, lo que puede reducir la latencia. Requiere administrador y reiniciar.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
             "HwSchMode", 2, 1)], admin=True, restart="pc"),
    Tweak("game_priority", O, "gaming", "Optimizar la prioridad del sistema para juegos",
          "Sube la prioridad de CPU/GPU de los juegos y reduce la reserva del sistema para tareas "
          "multimedia, priorizando el juego activo. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
             "SystemResponsiveness", 0, 20),
           E("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
             "Priority", 6, 2),
           E("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
             "Scheduling Category", "High", "Medium", SZ),
           E("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
             "SFIO Priority", "High", "Normal", SZ)], admin=True),

    # ------------------------------- Sistema -------------------------------
    Tweak("long_paths", O, "system", "Habilitar rutas largas (más de 260 caracteres)",
          "Levanta el límite histórico de 260 caracteres en las rutas de archivo, para apps y "
          "herramientas compatibles (Git, Node, etc.). Requiere administrador.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\FileSystem",
             "LongPathsEnabled", 1, 0)], admin=True),
    Tweak("ntfs_lastaccess", O, "system", "Desactivar la marca de 'último acceso' NTFS",
          "Evita que NTFS escriba la fecha de 'último acceso' cada vez que se abre un archivo, "
          "reduciendo escrituras en disco. Requiere administrador.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\FileSystem",
             "NtfsDisableLastAccessUpdate", 1, 0)], admin=True),
    Tweak("no_auto_reboot", O, "system", "Evitar el reinicio automático tras actualizaciones",
          "Tras instalar actualizaciones, Windows no reiniciará solo mientras haya alguien con la "
          "sesión iniciada (evita perder trabajo). Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU",
             "NoAutoRebootWithLoggedOnUsers", 1, 0)], admin=True),
    Tweak("uac_quiet", O, "system", "Reducir los avisos de UAC (menos seguro)",
          "El Control de cuentas (UAC) deja de oscurecer la pantalla y de pedir confirmación al "
          "ejecutar tareas como administrador. ATENCIÓN: REDUCE LA SEGURIDAD frente a malware. "
          "Requiere administrador y reiniciar.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
             "ConsentPromptBehaviorAdmin", 0, 5),
           E("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
             "PromptOnSecureDesktop", 0, 1)], admin=True, restart="pc", danger=True),
    Tweak("disable_smartscreen", O, "system", "Desactivar SmartScreen (menos seguro)",
          "Desactiva el filtro SmartScreen que avisa al abrir apps y archivos descargados poco "
          "habituales. ATENCIÓN: REDUCE LA SEGURIDAD frente a descargas maliciosas. Requiere administrador y reiniciar.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
             "SmartScreenEnabled", "Off", "RequireAdmin", SZ),
           E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",
             "EnableSmartScreen", 0, 1)], admin=True, restart="pc", danger=True),

    # =======================================================================
    # ===================== AMPLIACIÓN v1.1 (nuevos) ========================
    # =======================================================================

    # --- Personalización / Explorador ---
    Tweak("hide_onedrive", P, "explorer", "Ocultar OneDrive del panel del Explorador",
          "Quita el icono de OneDrive de la columna izquierda del Explorador (no desinstala OneDrive, "
          "solo lo oculta de la navegación).",
          [E("HKCU", r"Software\Classes\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}",
             "System.IsPinnedToNameSpaceTree", 0, 1),
           E("HKCU", r"Software\Classes\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}",
             "System.IsPinnedToNameSpaceTree", 0, 1)], restart="explorer"),
    Tweak("hide_gallery", P, "explorer", "Ocultar 'Galería' del Explorador",
          "Quita el elemento 'Galería' (la vista de fotos recientes) de la columna izquierda del "
          "Explorador, si tu versión de Windows 11 lo incluye.",
          [E("HKCU", r"Software\Classes\CLSID\{e88865ea-0e1c-4e20-9aa6-edcd0212c87c}",
             "System.IsPinnedToNameSpaceTree", 0, 1)], restart="explorer"),
    Tweak("context_cmd", P, "explorer", "Añadir 'Abrir símbolo del sistema aquí'",
          "Añade al menú del clic derecho (sobre el fondo de una carpeta) la opción para abrir el "
          "Símbolo del sistema directamente en esa ruta.",
          [E("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_cmd",
             "", "Abrir símbolo del sistema aquí", DELETE, SZ),
           E("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_cmd",
             "Icon", "cmd.exe", DELETE, SZ),
           E("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_cmd\command",
             "", r'cmd.exe /s /k pushd "%V"', DELETE, SZ)],
          cleanup_keys=[("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_cmd")]),
    Tweak("context_pwsh", P, "explorer", "Añadir 'Abrir PowerShell aquí'",
          "Añade al menú del clic derecho (sobre el fondo de una carpeta) la opción para abrir "
          "PowerShell directamente situado en esa ruta.",
          [E("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_pwsh",
             "", "Abrir PowerShell aquí", DELETE, SZ),
           E("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_pwsh",
             "Icon", "powershell.exe", DELETE, SZ),
           E("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_pwsh\command",
             "", r"powershell.exe -noexit -command Set-Location -LiteralPath '%V'", DELETE, SZ)],
          cleanup_keys=[("HKCU", r"Software\Classes\Directory\Background\shell\REPTOSX_pwsh")]),

    # --- Personalización / Barra de tareas ---
    Tweak("widgets_policy", P, "taskbar", "Desactivar Widgets por completo",
          "Desactiva la función de Widgets a nivel de sistema mediante directiva (más efectivo que "
          "solo ocultar el botón): elimina el panel de clima y noticias. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Dsh", "AllowNewsAndInterests", 0, 1)],
          admin=True, restart="explorer"),

    # --- Personalización / Escritorio e iconos ---
    Tweak("desktop_hide_spotlight", P, "desktop_icons", "Ocultar el icono de Spotlight del escritorio",
          "Quita del escritorio el icono 'Más información sobre esta imagen' que aparece cuando usas "
          "Windows Spotlight como fondo.",
          [E("HKCU", NEWSTART, "{2cc5ca98-6485-489a-920e-b3e88a6ccce3}", 1, 0)], restart="explorer"),

    # --- Optimización / Rendimiento ---
    Tweak("power_plan_high", O, "performance", "Plan de energía: Alto rendimiento",
          "Activa el plan de energía 'Alto rendimiento' de Windows con el comando powercfg "
          "(no apaga la pantalla/disco para priorizar el rendimiento). Al desactivarlo vuelve "
          "a 'Equilibrado'. Requiere administrador.",
          [], admin=True, is_on_fn=_power_is_high, apply_fn=_power_set),
    Tweak("power_throttling", O, "performance", "Desactivar la limitación de energía (Power Throttling)",
          "Impide que Windows reduzca la frecuencia de la CPU para ahorrar energía en apps en segundo "
          "plano. Útil en sobremesa para máximo rendimiento. Requiere administrador y reiniciar.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling",
             "PowerThrottlingOff", 1, 0)], admin=True, restart="pc"),
    Tweak("background_apps", O, "performance", "Desactivar las apps en segundo plano",
          "Impide que las aplicaciones de la Tienda se ejecuten en segundo plano (Windows 11 quitó el "
          "interruptor global de Configuración). Ahorra RAM, CPU y batería.",
          [E("HKCU", r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
             "GlobalUserDisabled", 1, 0),
           E("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Search",
             "BackgroundAppGlobalToggle", 0, 1)]),

    # --- Optimización / Arranque y apagado ---
    Tweak("first_logon_anim", O, "boot_shutdown", "Desactivar la animación de bienvenida",
          "Quita la animación de 'Preparando Windows / Hola' que se muestra la primera vez que cada "
          "usuario inicia sesión, acelerando ese arranque. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
             "EnableFirstLogonAnimation", 0, 1)], admin=True),

    # --- Optimización / Privacidad y telemetría ---
    Tweak("disable_diagtrack", O, "privacy", "Desactivar el servicio de telemetría (DiagTrack)",
          "Pone en 'Deshabilitado' el servicio DiagTrack ('Experiencias del usuario conectado y "
          "telemetría'), que recopila y envía datos de uso a Microsoft. Requiere administrador y reiniciar.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4, 2)],
          admin=True, restart="pc"),
    Tweak("disable_consumer_features", O, "privacy", "Bloquear apps promocionadas",
          "Bloquea por directiva la instalación automática de apps promocionadas y el contenido de "
          "consumidor (sugerencias en Inicio). En ediciones Home puede ignorarse. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\CloudContent",
             "DisableWindowsConsumerFeatures", 1, DELETE),
           E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\CloudContent",
             "DisableConsumerAccountStateContent", 1, DELETE)], admin=True),
    Tweak("disable_spotlight_features", O, "privacy", "Desactivar Windows Spotlight",
          "Desactiva por directiva todas las funciones de Windows Spotlight (fondos rotativos, datos "
          "curiosos y sugerencias en pantalla de bloqueo y escritorio). Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\CloudContent",
             "DisableWindowsSpotlightFeatures", 1, DELETE)], admin=True),

    # --- Optimización / Red ---
    Tweak("network_throttling", O, "network", "Desactivar la limitación de red (multimedia)",
          "Quita el límite de ~10 paquetes/ms que Windows aplica a la red para reservar CPU a tareas "
          "multimedia; útil en conexiones rápidas y juegos online. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
             "NetworkThrottlingIndex", 0xFFFFFFFF, 10)], admin=True),
    Tweak("disable_nagle", O, "network", "Desactivar el algoritmo de Nagle (menos latencia)",
          "Hace que la red envíe los paquetes pequeños al instante en vez de agruparlos unos "
          "milisegundos para ahorrar tráfico (algoritmo de Nagle). Reduce la latencia percibida en "
          "juegos online. Se aplica a todos los adaptadores de red detectados. Requiere administrador y reiniciar.",
          [], admin=True, restart="pc", is_on_fn=_nagle_is_on, apply_fn=_nagle_set),

    # --- Optimización / Juegos ---
    Tweak("fso_off", O, "gaming", "Desactivar optimizaciones de pantalla completa (FSO)",
          "Hace que los juegos a pantalla completa usen el modo exclusivo en lugar de las "
          "'optimizaciones de pantalla completa' de Windows, lo que suele reducir el input lag.",
          [E("HKCU", r"System\GameConfigStore", "GameDVR_HonorUserFSEBehaviorMode", 1, 0),
           E("HKCU", r"System\GameConfigStore", "GameDVR_DXGIHonorFSEWindowsCompatible", 1, 0),
           E("HKCU", r"System\GameConfigStore", "GameDVR_EFSEFeatureFlags", 0, 1)]),
    Tweak("sticky_keys", O, "gaming", "Desactivar el aviso de teclas especiales",
          "Quita la ventana de 'teclas especiales' que aparece al pulsar Mayús 5 veces seguidas "
          "y que interrumpe los juegos en pleno combate.",
          [E("HKCU", r"Control Panel\Accessibility\StickyKeys", "Flags", "506", "510", SZ),
           E("HKCU", r"Control Panel\Accessibility\ToggleKeys", "Flags", "58", "62", SZ)]),
    Tweak("vbs_off", O, "gaming", "Desactivar VBS / Integridad de memoria (más FPS)",
          "Desactiva la Seguridad basada en virtualización (VBS/HVCI, 'Integridad de memoria'), que "
          "puede costar entre un 5% y un 25% de FPS. ATENCIÓN: REDUCE LA SEGURIDAD. Requiere administrador y reiniciar.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity",
             "Enabled", 0, 1),
           E("HKLM", r"SYSTEM\CurrentControlSet\Control\DeviceGuard",
             "EnableVirtualizationBasedSecurity", 0, 1)], admin=True, restart="pc", danger=True),

    # --- Optimización / Sistema ---
    Tweak("reserved_storage_off", O, "system", "Desactivar el almacenamiento reservado",
          "Indica a Windows que no reserve ~7 GB de disco para futuras actualizaciones; el espacio se "
          "libera tras la siguiente actualización de características. Requiere administrador.",
          [E("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\ReserveManager",
             "ShippedWithReserves", 0, 1)], admin=True, restart="pc"),
    Tweak("disable_sysmain", O, "system", "Desactivar el servicio SysMain (Superfetch)",
          "Pone en 'Deshabilitado' el servicio SysMain (antes Superfetch), que precarga apps en RAM. "
          "Recomendado en discos SSD, donde aporta poco y genera escrituras. Requiere administrador y reiniciar.",
          [E("HKLM", r"SYSTEM\CurrentControlSet\Services\SysMain", "Start", 4, 2)],
          admin=True, restart="pc"),
]


# Presets: cada uno activa (True) o desactiva (False) una lista de ajustes por id.
PRESETS = [
    {"id": "gaming", "icon": "🎮", "name": "Gaming",
     "desc": "Máximo rendimiento para juegos: prioridad, GPU por hardware, red sin latencia extra "
             "y sin telemetría/tareas de fondo que roben recursos.",
     "set": {"disable_game_dvr": True, "hags": True, "sticky_keys": True,
             "game_priority": True, "network_throttling": True, "fso_off": True,
             "foreground_priority": True, "visual_fx_perf": True,
             "startup_delay": True, "power_plan_high": True, "background_apps": True,
             "power_throttling": True, "mouse_accel": True, "qos_bandwidth": True,
             "disable_delivery_opt": True, "disable_diagtrack": True,
             "disable_recall": True, "disable_nagle": True}},
    {"id": "privacy", "icon": "🔒", "name": "Privacidad máxima",
     "desc": "Desactiva telemetría, sugerencias, Recall, búsqueda web y rastreo de escritura.",
     "set": {"disable_suggested": True, "stop_app_reinstall": True,
             "disable_input_personalization": True, "disable_feedback": True, "disable_scoobe": True,
             "disable_bing": True, "lockscreen_tips": True, "disable_telemetry": True,
             "disable_recall": True, "disable_websearch": True, "disable_diagtrack": True,
             "disable_consumer_features": True, "disable_spotlight_features": True}},
    {"id": "minimal", "icon": "🌙", "name": "Escritorio minimalista",
     "desc": "Modo oscuro total y limpieza visual real: sin Widgets ni buscador en la "
             "barra, Explorador y menú Inicio sin sugerencias, escritorio y bloqueo limpios.",
     "set": {"dark_apps": True, "dark_system": True, "hide_taskview": True,
             "hide_search": True, "widgets_policy": True, "compact_mode": True,
             "disable_suggested": True, "start_track_docs": True, "hide_quickaccess": True,
             "hide_onedrive": True, "hide_gallery": True, "desktop_hide_recyclebin": True,
             "remove_shortcut_suffix": True, "lockscreen_tips": True}},
    {"id": "clean", "icon": "🧹", "name": "Limpio y rápido",
     "desc": "Quita bloatware y sugerencias y acelera el sistema sin tocar la privacidad a fondo.",
     "set": {"disable_suggested": True, "stop_app_reinstall": True,
             "disable_consumer_features": True, "startup_delay": True, "menu_delay": True,
             "visual_fx_perf": True, "disable_game_dvr": True, "ntfs_lastaccess": True,
             "background_apps": True}},
]


def tweak_by_id(tid):
    for t in TWEAKS:
        if t.id == tid:
            return t
    return None


def grouped():
    """Devuelve [(grupo, [categorías...]), ...] en orden de aparición."""
    result = []
    for g in GROUPS:
        cats = []
        for t in TWEAKS:
            if t.group == g and t.category not in cats:
                cats.append(t.category)
        result.append((g, cats))
    return result


def first_category():
    return grouped()[0][1][0]
