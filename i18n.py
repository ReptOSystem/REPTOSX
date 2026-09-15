"""Sistema de idiomas de REPTOSX (Español / English).

Español es el idioma por defecto. El idioma activo se guarda como estado de
módulo (ver get_lang/set_lang) y el resto de la app lo consulta en tiempo
real mediante tr() (textos de interfaz) y las funciones tweak_name/
tweak_desc/preset_name/preset_desc/category_label/group_label.

Los textos en español de cada ajuste y preset viven en tweaks_data.py como
antes (son el idioma por defecto, no hay que duplicarlos aquí). Aquí solo
se guardan las traducciones al inglés, indexadas por el `id` estable de
cada ajuste/preset.
"""

LANGUAGES = ["es", "en"]
LANG_NAMES = {"es": "Español", "en": "English"}

_lang = "es"


def get_lang() -> str:
    return _lang


def set_lang(code: str) -> None:
    global _lang
    if code in LANGUAGES:
        _lang = code


def tr(key: str, **kwargs) -> str:
    """Texto de interfaz en el idioma activo, con formato opcional (.format)."""
    table = UI_STRINGS.get(_lang, UI_STRINGS["es"])
    text = table.get(key, UI_STRINGS["es"].get(key, key))
    return text.format(**kwargs) if kwargs else text


def category_label(key: str) -> str:
    return CATEGORY_LABELS.get(_lang, CATEGORY_LABELS["es"]).get(key, key)


def group_label(key: str) -> str:
    return GROUP_LABELS.get(_lang, GROUP_LABELS["es"]).get(key, key)


def tweak_name(tweak) -> str:
    if _lang == "en" and tweak.id in TWEAK_EN:
        return TWEAK_EN[tweak.id]["name"]
    return tweak._name_es


def tweak_desc(tweak) -> str:
    if _lang == "en" and tweak.id in TWEAK_EN:
        return TWEAK_EN[tweak.id]["desc"]
    return tweak._desc_es


def preset_name(preset: dict) -> str:
    if _lang == "en" and preset["id"] in PRESET_EN:
        return PRESET_EN[preset["id"]]["name"]
    return preset["name"]


def preset_desc(preset: dict) -> str:
    if _lang == "en" and preset["id"] in PRESET_EN:
        return PRESET_EN[preset["id"]]["desc"]
    return preset["desc"]


# ============================================================================
# Categorías y grupos: claves internas estables (no se traducen ni se
# muestran directamente) -> etiqueta visible en cada idioma.
# ============================================================================
CATEGORY_LABELS = {
    "es": {
        "appearance": "Apariencia",
        "taskbar": "Barra de tareas",
        "start_menu": "Menú Inicio",
        "explorer": "Explorador",
        "desktop_icons": "Escritorio e iconos",
        "lock_screen": "Pantalla de bloqueo",
        "performance": "Rendimiento",
        "boot_shutdown": "Arranque y apagado",
        "privacy": "Privacidad y telemetría",
        "network": "Red",
        "gaming": "Juegos",
        "system": "Sistema",
    },
    "en": {
        "appearance": "Appearance",
        "taskbar": "Taskbar",
        "start_menu": "Start Menu",
        "explorer": "File Explorer",
        "desktop_icons": "Desktop & Icons",
        "lock_screen": "Lock Screen",
        "performance": "Performance",
        "boot_shutdown": "Startup & Shutdown",
        "privacy": "Privacy & Telemetry",
        "network": "Network",
        "gaming": "Gaming",
        "system": "System",
    },
}

GROUP_LABELS = {
    "es": {"personalization": "Personalización", "optimization": "Optimización"},
    "en": {"personalization": "Personalization", "optimization": "Optimization"},
}


# ============================================================================
# Textos de la interfaz (main.py). Español = valor por defecto/fallback.
# ============================================================================
UI_STRINGS = {
    "es": {
        "app.title": "REPTOSX  ·  Herramienta de personalización de Windows 11",
        "sidebar.tagline": "para Windows 11",
        "nav.presets": "Presets",
        "nav.my_pc": "Mi equipo",
        "nav.restore_point": "Punto de restauración",
        "nav.about": "Acerca de REPTOSX",
        "sidebar.theme_label": "TEMA DE LA APP",
        "sidebar.lang_label": "IDIOMA",
        "topbar.search_placeholder": "Buscar ajuste...",
        "topbar.restart_explorer": "Reiniciar Explorador",
        "topbar.restart_explorer_pending": "Reiniciar Explorador  •",
        "topbar.restart_as_admin": "🛡  Reiniciar como admin",
        "content.filter_active_only": "Solo activados",
        "content.restore_category": "Restaurar categoría",
        "content.active_count": "{active}/{total} activados",
        "status.mode_admin": "Administrador",
        "status.mode_standard": "Usuario estándar (ajustes del sistema bloqueados)",
        "status.ready": "  Listo  ·  Modo: {mode}  ·  {count} ajustes disponibles",
        "search.no_results": "Sin resultados para la búsqueda.",
        "category.no_active": "No hay ajustes activados en esta categoría.",
        "search.results_of": "Resultados de '{query}'",
        "presets.title": "Presets",
        "presets.intro": "Aplica varios ajustes a la vez con un clic. Cada preset muestra qué cambia.  "
                         "🔒 requiere administrador (se omite si no lo eres)   ⚠ reduce la seguridad.",
        "presets.changes_count": "CAMBIA {n} AJUSTES",
        "presets.apply_button": "Aplicar",
        "presets.my_config_label": "TU CONFIGURACIÓN",
        "presets.export_button": "Exportar mi configuración",
        "presets.import_button": "Importar configuración",
        "presets.restore_all_button": "Restaurar TODO a los valores predeterminados",
        "sysinfo.title": "Mi equipo",
        "sysinfo.intro": "Especificaciones detectadas de tu equipo. Nada de esto se envía a "
                         "ningún sitio: se lee y se muestra solo aquí.",
        "sysinfo.cpu_title": "Procesador",
        "sysinfo.cpu_threads": "{name}  ·  {threads} hilos lógicos",
        "sysinfo.ram_title": "Memoria RAM",
        "sysinfo.ram_usage": "{used:.1f} GB usados de {total:.1f} GB  ({percent}%)",
        "sysinfo.gpu_title": "Tarjeta gráfica",
        "sysinfo.gpu_vram": "  ·  {vram} GB de VRAM",
        "sysinfo.disk_title": "Disco ({letter})",
        "sysinfo.disk_usage": "{free:.0f} GB libres de {total:.0f} GB",
        "sysinfo.os_title": "Sistema operativo",
        "sysinfo.os_version": "  ·  versión {version}",
        "sysinfo.disks_physical_label": "DISCOS FÍSICOS",
        "sysinfo.detecting_disk_type": "Detectando tipo de disco (SSD/HDD)...",
        "sysinfo.disk_type_unavailable": "No se pudo detectar (no disponible en esta edición de Windows).",
        "disclaimer.title_bar": "Aviso importante  ·  REPTOSX",
        "disclaimer.header": "Aviso importante",
        "disclaimer.subtitle": "Lee y acepta antes de continuar",
        "disclaimer.body": (
            "REPTOSX modifica ajustes del Registro y del sistema de Windows.\n\n"
            "• La gran mayoría de las funciones son completamente seguras y reversibles.\n"
            "• En cada ajuste se detalla exactamente qué hace antes de aplicarlo.\n"
            "• Algunos ajustes (marcados con ⚠) reducen la seguridad: la app te\n"
            "   pedirá confirmación antes de aplicarlos.\n\n"
            "Aun así, cualquier cambio que realices es BAJO TU PROPIA RESPONSABILIDAD. "
            "Se recomienda crear un punto de restauración antes de hacer cambios "
            "importantes (tienes un botón para ello en la barra lateral). El autor no se "
            "responsabiliza de posibles problemas derivados del uso de la herramienta.\n\n"
            "Al pulsar \"Acepto y continúo\" confirmas que entiendes y aceptas estas condiciones."
        ),
        "disclaimer.checkbox": "No volver a mostrar este aviso",
        "disclaimer.exit_button": "Salir",
        "disclaimer.accept_button": "Acepto y continúo",
        "confirm.security_title": "Ajuste de seguridad",
        "confirm.security_message": (
            "'{name}' REDUCE la seguridad de Windows.\n\n"
            "Solo deberías activarlo si sabes lo que haces. Es reversible."
        ),
        "status.admin_required": "Este ajuste requiere ejecutar la app como administrador.",
        "status.permission_denied": "Permiso denegado. Ejecuta la app como administrador.",
        "status.error_generic": "Error: {error}",
        "status.apply_failed": "No se pudo aplicar '{name}': {error}",
        "status.turned_on": "activado",
        "status.turned_off": "desactivado",
        "status.tweak_toggled": "'{name}' {state}.",
        "status.tweak_toggled_explorer": "'{name}' {state}. Reinicia el Explorador para verlo.",
        "status.tweak_toggled_pc": "'{name}' {state}. Reinicia el PC para aplicar el cambio.",
        "card.restart_explorer_note": "   ·  Reinicia el Explorador para verlo.",
        "card.restart_pc_note": "   ·  Requiere reiniciar el PC.",
        "confirm.restore_category_title": "Restaurar categoría",
        "confirm.restore_category_status": "Categoría '{cat}' restaurada",
        "confirm.restore_category_note": "Se restaurarán a su valor predeterminado todos los ajustes de '{cat}'.",
        "confirm.restore_all_title": "Restaurar TODO",
        "confirm.restore_all_status": "Todos los ajustes restaurados",
        "confirm.restore_all_note": "Se restaurarán TODOS los ajustes a sus valores predeterminados de Windows. "
                                    "Esta acción es reversible volviendo a activarlos.",
        "confirm.apply_preset_title": "Aplicar preset '{name}'",
        "bulk.no_changes": "{title}: no hay cambios que aplicar, ya coincide con tu configuración actual.",
        "bulk.will_change": "Se van a cambiar {n} ajuste{plural}.",
        "bulk.danger_warning": "\n\n⚠ Esto también ACTIVARÁ ajustes que reducen la seguridad de Windows:\n{names}",
        "bulk.suggest_restore_point": "\n\nConsejo: como son varios cambios a la vez, crea antes un punto de "
                                      "restauración (botón en la barra lateral) por si acaso.",
        "bulk.applied": "{title}: {n} ajustes aplicados",
        "bulk.skipped_admin": ", {n} omitidos (requieren administrador)",
        "bulk.restart_pc_needed": ". Reinicia el PC para completar.",
        "export.dialog_title": "Exportar configuración de REPTOSX",
        "export.file_type_label": "Perfil de REPTOSX",
        "export.status_success": "Configuración exportada a '{filename}'.",
        "export.status_error": "No se pudo exportar la configuración: {error}",
        "import.dialog_title": "Importar configuración de REPTOSX",
        "import.all_files_label": "Todos los archivos",
        "import.read_error": "No se pudo leer el archivo: {error}",
        "import.invalid_format": "El archivo no tiene un formato de perfil de REPTOSX válido.",
        "import.no_recognized": "El archivo no contiene ningún ajuste reconocido por esta versión.",
        "import.note": "Se aplicará la configuración guardada en '{filename}' ({n} ajustes reconocidos).",
        "import.unknown_note": " Se ignorarán {n} ajustes no reconocidos (de otra versión de REPTOSX).",
        "import.confirm_title": "Importar perfil",
        "import.status_title": "Perfil '{filename}' importado",
        "confirm.cancel_button": "Cancelar",
        "confirm.default_button": "Confirmar",
        "theme.apply_status": "Tema '{name}' aplicado.",
        "lang.apply_status": "Idioma cambiado a {name}.",
        "explorer.restarted_status": "Explorador reiniciado. Los cambios visuales ya están aplicados.",
        "explorer.restart_error": "No se pudo reiniciar el Explorador: {error}",
        "restore_point.admin_required": "Crear un punto de restauración requiere ejecutar la app como administrador.",
        "restore_point.already_running": "Ya se está creando un punto de restauración, espera un momento...",
        "restore_point.confirm_title": "Crear punto de restauración",
        "restore_point.confirm_message": (
            "Se creará un punto de restauración del sistema llamado 'REPTOSX'. "
            "Puede tardar un momento. Si algo saliera mal, podrás volver a este punto "
            "desde 'Recuperación' en el Panel de control."
        ),
        "restore_point.creating_status": "Creando punto de restauración... (puede tardar un poco)",
        "restore_point.success": "Punto de restauración 'REPTOSX' creado correctamente.",
        "restore_point.frequency_error": "Windows solo permite un punto de restauración cada 24 h "
                                         "(o Restaurar sistema está desactivado).",
        "restore_point.generic_error": "No se pudo crear el punto: {detail}",
        "channel.opening_status": "Abriendo el canal de YouTube de reptOSystem...",
        "about.title_bar": "Acerca de REPTOSX",
        "about.subtitle": "Herramienta de personalización y optimización para Windows 11",
        "about.description": (
            "REPTOSX reúne en un solo lugar los ajustes del Registro de Windows 11 "
            "que normalmente se cambian a mano para personalizar y optimizar el sistema: "
            "apariencia, barra de tareas, Explorador, menú Inicio, rendimiento, "
            "privacidad y opciones del sistema.\n\n"
            "Todo desde una interfaz cómoda, con un interruptor por ajuste y la posibilidad "
            "de revertir cada cambio a su valor predeterminado.\n\n"
            "Creada por reptOSystem, creador de contenido sobre personalización y "
            "optimización de Windows. En el canal encontrarás guías, trucos y tutoriales "
            "para sacarle el máximo partido a tu PC."
        ),
        "about.channel_label": "Canal de YouTube",
        "about.visit_button": "▶  Visitar el canal de reptOSystem",
        "about.version_footer": "Versión 1.0  ·  Hecho con ❤️ para la comunidad de Windows",
        "elevate.error": "No se pudo elevar: {error}",
    },
    "en": {
        "app.title": "REPTOSX  ·  Windows 11 Customization Tool",
        "sidebar.tagline": "for Windows 11",
        "nav.presets": "Presets",
        "nav.my_pc": "My PC",
        "nav.restore_point": "Restore Point",
        "nav.about": "About REPTOSX",
        "sidebar.theme_label": "APP THEME",
        "sidebar.lang_label": "LANGUAGE",
        "topbar.search_placeholder": "Search a tweak...",
        "topbar.restart_explorer": "Restart Explorer",
        "topbar.restart_explorer_pending": "Restart Explorer  •",
        "topbar.restart_as_admin": "🛡  Restart as admin",
        "content.filter_active_only": "Active only",
        "content.restore_category": "Restore category",
        "content.active_count": "{active}/{total} active",
        "status.mode_admin": "Administrator",
        "status.mode_standard": "Standard user (system tweaks locked)",
        "status.ready": "  Ready  ·  Mode: {mode}  ·  {count} tweaks available",
        "search.no_results": "No results for this search.",
        "category.no_active": "No tweaks are active in this category.",
        "search.results_of": "Results for '{query}'",
        "presets.title": "Presets",
        "presets.intro": "Apply several tweaks at once with one click. Each preset shows what it changes.  "
                         "🔒 requires administrator (skipped if you're not one)   ⚠ reduces security.",
        "presets.changes_count": "CHANGES {n} TWEAKS",
        "presets.apply_button": "Apply",
        "presets.my_config_label": "YOUR CONFIGURATION",
        "presets.export_button": "Export my configuration",
        "presets.import_button": "Import configuration",
        "presets.restore_all_button": "Restore ALL to default values",
        "sysinfo.title": "My PC",
        "sysinfo.intro": "Specs detected on your PC. None of this is sent anywhere: "
                         "it's only read and shown here.",
        "sysinfo.cpu_title": "Processor",
        "sysinfo.cpu_threads": "{name}  ·  {threads} logical threads",
        "sysinfo.ram_title": "RAM Memory",
        "sysinfo.ram_usage": "{used:.1f} GB used of {total:.1f} GB  ({percent}%)",
        "sysinfo.gpu_title": "Graphics card",
        "sysinfo.gpu_vram": "  ·  {vram} GB of VRAM",
        "sysinfo.disk_title": "Drive ({letter})",
        "sysinfo.disk_usage": "{free:.0f} GB free of {total:.0f} GB",
        "sysinfo.os_title": "Operating system",
        "sysinfo.os_version": "  ·  version {version}",
        "sysinfo.disks_physical_label": "PHYSICAL DRIVES",
        "sysinfo.detecting_disk_type": "Detecting drive type (SSD/HDD)...",
        "sysinfo.disk_type_unavailable": "Could not be detected (not available on this Windows edition).",
        "disclaimer.title_bar": "Important notice  ·  REPTOSX",
        "disclaimer.header": "Important notice",
        "disclaimer.subtitle": "Read and accept before continuing",
        "disclaimer.body": (
            "REPTOSX modifies Windows Registry and system settings.\n\n"
            "• The vast majority of features are completely safe and reversible.\n"
            "• Every tweak explains exactly what it does before you apply it.\n"
            "• Some tweaks (marked with ⚠) reduce security: the app will\n"
            "   ask for confirmation before applying them.\n\n"
            "Even so, any change you make is YOUR OWN RESPONSIBILITY. "
            "We recommend creating a restore point before making major "
            "changes (there's a button for that in the sidebar). The author is not "
            "responsible for any issues arising from the use of this tool.\n\n"
            "By clicking \"I accept and continue\" you confirm that you understand and accept these terms."
        ),
        "disclaimer.checkbox": "Don't show this notice again",
        "disclaimer.exit_button": "Exit",
        "disclaimer.accept_button": "I accept and continue",
        "confirm.security_title": "Security tweak",
        "confirm.security_message": (
            "'{name}' REDUCES Windows security.\n\n"
            "Only enable it if you know what you're doing. It's reversible."
        ),
        "status.admin_required": "This tweak requires running the app as administrator.",
        "status.permission_denied": "Permission denied. Run the app as administrator.",
        "status.error_generic": "Error: {error}",
        "status.apply_failed": "Could not apply '{name}': {error}",
        "status.turned_on": "enabled",
        "status.turned_off": "disabled",
        "status.tweak_toggled": "'{name}' {state}.",
        "status.tweak_toggled_explorer": "'{name}' {state}. Restart Explorer to see it.",
        "status.tweak_toggled_pc": "'{name}' {state}. Restart your PC to apply the change.",
        "card.restart_explorer_note": "   ·  Restart Explorer to see it.",
        "card.restart_pc_note": "   ·  Requires restarting your PC.",
        "confirm.restore_category_title": "Restore category",
        "confirm.restore_category_status": "Category '{cat}' restored",
        "confirm.restore_category_note": "All tweaks in '{cat}' will be restored to their default values.",
        "confirm.restore_all_title": "Restore ALL",
        "confirm.restore_all_status": "All tweaks restored",
        "confirm.restore_all_note": "ALL tweaks will be restored to Windows default values. "
                                    "This action is reversible by turning them on again.",
        "confirm.apply_preset_title": "Apply preset '{name}'",
        "bulk.no_changes": "{title}: nothing to apply, it already matches your current configuration.",
        "bulk.will_change": "{n} tweak{plural} will be changed.",
        "bulk.danger_warning": "\n\n⚠ This will also ENABLE tweaks that reduce Windows security:\n{names}",
        "bulk.suggest_restore_point": "\n\nTip: since this changes several tweaks at once, create a restore "
                                      "point first (button in the sidebar) just in case.",
        "bulk.applied": "{title}: {n} tweaks applied",
        "bulk.skipped_admin": ", {n} skipped (require administrator)",
        "bulk.restart_pc_needed": ". Restart your PC to finish.",
        "export.dialog_title": "Export REPTOSX configuration",
        "export.file_type_label": "REPTOSX profile",
        "export.status_success": "Configuration exported to '{filename}'.",
        "export.status_error": "Could not export the configuration: {error}",
        "import.dialog_title": "Import REPTOSX configuration",
        "import.all_files_label": "All files",
        "import.read_error": "Could not read the file: {error}",
        "import.invalid_format": "This file is not a valid REPTOSX profile.",
        "import.no_recognized": "This file has no tweaks recognized by this version.",
        "import.note": "The configuration saved in '{filename}' will be applied ({n} recognized tweaks).",
        "import.unknown_note": " {n} unrecognized tweaks will be ignored (from another REPTOSX version).",
        "import.confirm_title": "Import profile",
        "import.status_title": "Profile '{filename}' imported",
        "confirm.cancel_button": "Cancel",
        "confirm.default_button": "Confirm",
        "theme.apply_status": "Theme '{name}' applied.",
        "lang.apply_status": "Language switched to {name}.",
        "explorer.restarted_status": "Explorer restarted. Visual changes are now applied.",
        "explorer.restart_error": "Could not restart Explorer: {error}",
        "restore_point.admin_required": "Creating a restore point requires running the app as administrator.",
        "restore_point.already_running": "A restore point is already being created, please wait...",
        "restore_point.confirm_title": "Create restore point",
        "restore_point.confirm_message": (
            "A system restore point named 'REPTOSX' will be created. "
            "This may take a moment. If something goes wrong, you can go back to this "
            "point from 'Recovery' in Control Panel."
        ),
        "restore_point.creating_status": "Creating restore point... (this may take a moment)",
        "restore_point.success": "Restore point 'REPTOSX' created successfully.",
        "restore_point.frequency_error": "Windows only allows one restore point every 24 h "
                                         "(or System Restore is turned off).",
        "restore_point.generic_error": "Could not create the restore point: {detail}",
        "channel.opening_status": "Opening reptOSystem's YouTube channel...",
        "about.title_bar": "About REPTOSX",
        "about.subtitle": "Windows 11 customization and optimization tool",
        "about.description": (
            "REPTOSX brings together, in one place, the Windows 11 Registry tweaks "
            "that are normally changed by hand to customize and optimize the system: "
            "appearance, taskbar, File Explorer, Start Menu, performance, "
            "privacy and system options.\n\n"
            "All from a comfortable interface, with one switch per tweak and the option "
            "to revert every change back to its default value.\n\n"
            "Created by reptOSystem, a content creator focused on Windows customization "
            "and optimization. On the channel you'll find guides, tricks and tutorials "
            "to get the most out of your PC."
        ),
        "about.channel_label": "YouTube channel",
        "about.visit_button": "▶  Visit reptOSystem's channel",
        "about.version_footer": "Version 1.0  ·  Made with ❤️ for the Windows community",
        "elevate.error": "Could not elevate: {error}",
    },
}


# ============================================================================
# Traducciones al inglés de cada ajuste (id -> name/desc). El español vive
# directamente en tweaks_data.py como valor por defecto.
# ============================================================================
TWEAK_EN = {
    # ---------------------------- Appearance --------------------------------
    "dark_apps": {
        "name": "Dark mode for apps",
        "desc": "Switches modern apps (Settings, File Explorer, Store...) to dark theme. "
                "Doesn't affect the taskbar or Start menu (that's the system dark mode).",
    },
    "dark_system": {
        "name": "Dark mode for the system",
        "desc": "Switches the taskbar, Start menu, notification center and system "
                "menus to dark theme.",
    },
    "wallpaper_quality": {
        "name": "Maximum wallpaper quality",
        "desc": "Makes Windows apply your desktop wallpaper without JPEG recompression "
                "(100% quality), avoiding loss of sharpness. Re-set your wallpaper after enabling it.",
    },
    "disable_shake": {
        "name": "Disable 'shake to minimize' (Aero Shake)",
        "desc": "When you grab and shake a window, Windows will no longer minimize all "
                "the others (avoids accidentally minimizing everything while moving windows).",
    },
    # -------------------------------- Taskbar --------------------------------
    "taskbar_left": {
        "name": "Align the taskbar to the left",
        "desc": "Aligns the icons and Start button to the left of the taskbar, "
                "like in Windows 10, instead of centered.",
    },
    "hide_taskview": {
        "name": "Hide the Task View button",
        "desc": "Hides the Task View button (virtual desktops) from the taskbar. "
                "The Win+Tab shortcut keeps working.",
    },
    "hide_search": {
        "name": "Hide the search box",
        "desc": "Completely hides the search box or icon from the taskbar. "
                "You can still search using the Windows key.",
    },
    "never_combine": {
        "name": "Never combine buttons (show labels)",
        "desc": "Every open window appears as its own independent button with its title, "
                "without grouping ('Never combine' mode from Windows 10). Needs Windows 11 23H2 or later.",
    },
    "tray_show_all": {
        "name": "Show all tray icons",
        "desc": "Always shows every icon in the notification area (next to the clock), "
                "without hiding them in the overflow menu (the little arrow).",
    },
    "end_task": {
        "name": "Add 'End task' to the right-click menu",
        "desc": "Adds the 'End task' option to the right-click menu on any app in the "
                "taskbar, so you can close it instantly. Needs Windows 11 23H2 or later.",
    },
    # ------------------------------ Start Menu -------------------------------
    "disable_bing": {
        "name": "Disable Bing web search in Start",
        "desc": "Removes internet and Bing results from the Start menu and the search "
                "box; search then only looks on your PC and is faster.",
    },
    "start_more_pins": {
        "name": "Start menu layout: more pinned apps",
        "desc": "Changes the Start menu layout to show more rows of pinned apps and "
                "shrink the 'Recommended' section.",
    },
    "start_track_docs": {
        "name": "Don't show recently opened items",
        "desc": "Stops showing recently opened files in the Start menu, in jump lists "
                "(right-click on taskbar icons) and in File Explorer's quick access.",
    },
    "start_account_notif": {
        "name": "Disable account notifications in Start",
        "desc": "Removes the notices and suggestions about your Microsoft account that "
                "appear above your name in the Start menu.",
    },
    "disable_copilot": {
        "name": "Disable Windows Copilot",
        "desc": "Disables the Windows Copilot assistant via policy: hides its button "
                "and prevents it from opening.",
    },
    # ------------------------------- Explorer --------------------------------
    "show_ext": {
        "name": "Show file extensions",
        "desc": "Shows the extension (.txt, .exe, .jpg...) of every file. Helps you "
                "spot deceptive files like 'photo.jpg.exe'.",
    },
    "show_hidden": {
        "name": "Show hidden files",
        "desc": "Shows files and folders marked with the 'hidden' attribute.",
    },
    "show_super_hidden": {
        "name": "Show protected system files",
        "desc": "Also shows files protected by the operating system (like pagefile.sys). "
                "Use with caution: don't delete what you don't recognize.",
    },
    "classic_menu": {
        "name": "Classic context menu (Windows 10 style)",
        "desc": "Brings back the full Windows 10 right-click menu, without having to "
                "click 'Show more options' to see everything.",
    },
    "compact_mode": {
        "name": "Compact view in File Explorer",
        "desc": "Reduces the spacing between files and folders so more items fit on "
                "screen (a look closer to Windows 10).",
    },
    "launch_thispc": {
        "name": "Open File Explorer in 'This PC'",
        "desc": "File Explorer opens showing 'This PC' (your drives) instead of the "
                "'Home / Quick access' page.",
    },
    "nav_expand": {
        "name": "Expand to the current folder in the sidebar",
        "desc": "The folder tree on the left automatically expands down to the folder "
                "you have open.",
    },
    "drive_letters_first": {
        "name": "Show the drive letter before the name",
        "desc": "Shows drives as '(C:) Local Disk' instead of 'Local Disk (C:)'.",
    },
    "hide_quickaccess": {
        "name": "Hide recent and frequent items in File Explorer",
        "desc": "Removes the list of recently used files and frequent folders from "
                "File Explorer's Home page (more privacy).",
    },
    "remove_shortcut_suffix": {
        "name": "Remove the '- Shortcut' text",
        "desc": "Shortcuts you create from now on will no longer add ' - Shortcut' "
                "to the end of the name.",
    },
    # --------------------------- Desktop & Icons -----------------------------
    "desktop_thispc": {
        "name": "Show 'This PC' on the desktop",
        "desc": "Adds the 'This PC' icon to the desktop so you can reach your drives "
                "with a double click.",
    },
    "desktop_userfolder": {
        "name": "Show your user folder",
        "desc": "Adds the icon for your personal folder (Documents, Downloads, "
                "Pictures...) to the desktop.",
    },
    "desktop_network": {
        "name": "Show 'Network' on the desktop",
        "desc": "Adds the 'Network' icon to the desktop (computers and shared "
                "resources on your local network).",
    },
    "desktop_controlpanel": {
        "name": "Show 'Control Panel' on the desktop",
        "desc": "Adds a shortcut to the classic Control Panel on the desktop.",
    },
    "desktop_hide_recyclebin": {
        "name": "Hide the Recycle Bin",
        "desc": "Removes the Recycle Bin icon from the desktop (you can still empty "
                "it from File Explorer).",
    },
    # ------------------------------ Lock Screen -------------------------------
    "lockscreen_tips": {
        "name": "Remove lock screen trivia and ads",
        "desc": "Removes the fun facts, tips and ads that Windows shows over the lock "
                "screen picture (Windows Spotlight).",
    },
    "no_lockscreen": {
        "name": "Disable the lock screen",
        "desc": "Skips the lock screen (the picture with the clock) and goes straight "
                "to sign-in. Requires administrator.",
    },
    "logon_blur": {
        "name": "Remove the sign-in screen blur",
        "desc": "Removes the blur (acrylic effect) from the background of the sign-in "
                "screen, showing the picture sharp. Requires administrator.",
    },
    # ----------------------------- Performance --------------------------------
    "visual_fx_perf": {
        "name": "Visual effects: adjust for performance",
        "desc": "Sets visual effects to 'Adjust for best performance': disables "
                "animations, shadows and transparency in the UI. Useful on modest PCs.",
    },
    "min_animate": {
        "name": "Disable window animations",
        "desc": "Removes the minimize/maximize window animation; windows appear instantly.",
    },
    "menu_delay": {
        "name": "Speed up menu opening",
        "desc": "Reduces the menu opening delay from 400 ms to 0 ms, making the "
                "interface feel snappier when hovering with the mouse.",
    },
    "startup_delay": {
        "name": "Remove the startup apps delay",
        "desc": "Removes the artificial delay (~10 s) Windows applies to startup "
                "programs, so they launch right after sign-in.",
    },
    "mouse_accel": {
        "name": "Disable mouse acceleration",
        "desc": "Disables 'enhance pointer precision', so the cursor moves 1:1 with "
                "the mouse (recommended for gaming and design work).",
    },
    "close_hung_apps": {
        "name": "Close unresponsive apps faster",
        "desc": "Reduces how long Windows waits before force-closing hung apps when "
                "shutting down or restarting, speeding up shutdown.",
    },
    "foreground_priority": {
        "name": "Prioritize the app in the foreground",
        "desc": "Gives more CPU time to the window you're currently using, improving "
                "its responsiveness over background apps. Requires administrator and a restart.",
    },
    # ------------------------- Startup & Shutdown -----------------------------
    "disable_fast_startup": {
        "name": "Disable Fast Startup",
        "desc": "Disables 'Fast Startup' (a partial hibernation of the system). "
                "Recommended if you dual-boot or have shutdown/startup issues. Requires administrator.",
    },
    "disable_hibernation": {
        "name": "Disable hibernation",
        "desc": "Disables the hibernate feature; doing so frees the hiberfil.sys file "
                "(several GB of disk space). Requires administrator and a restart.",
    },
    "wait_kill_service": {
        "name": "Speed up closing services on shutdown",
        "desc": "Reduces from 5 s to 2 s how long Windows waits for each service before "
                "closing it on shutdown, shortening shutdown time. Requires administrator.",
    },
    "startup_sound": {
        "name": "Disable the Windows startup sound",
        "desc": "Mutes the sound Windows plays when starting up and signing in. Requires administrator.",
    },
    "verbose_status": {
        "name": "Detailed status messages",
        "desc": "Shows detailed messages ('Starting services...', etc.) during startup "
                "and shutdown, instead of just 'Welcome'. Useful for diagnosing slowdowns. Requires administrator.",
    },
    # ---------------------------- Privacy & Telemetry --------------------------
    "disable_suggested": {
        "name": "Disable suggested content and tips",
        "desc": "Removes app suggestions, ads and 'tips' that Windows shows in the "
                "Start menu, Settings and the timeline.",
    },
    "stop_app_reinstall": {
        "name": "Prevent reinstalling suggested apps",
        "desc": "Stops Windows from 'surprise' installing promoted apps and bloatware "
                "(games, TikTok, etc.) on your account automatically.",
    },
    "disable_input_personalization": {
        "name": "Disable typing data collection",
        "desc": "Prevents Windows from collecting and sending samples of your typing, "
                "voice and handwriting for 'personalization'.",
    },
    "disable_feedback": {
        "name": "Disable feedback requests",
        "desc": "Windows stops periodically showing you windows asking for your "
                "opinion (Feedback Hub).",
    },
    "disable_scoobe": {
        "name": "Remove 'Let's finish setting up your device'",
        "desc": "Disables the full-screen prompt that, after an update, nags you to "
                "set up OneDrive, Microsoft 365, etc.",
    },
    "disable_telemetry": {
        "name": "Reduce telemetry to the minimum",
        "desc": "Sets the diagnostic data sent to Microsoft to the lowest possible "
                "level (on Home/Pro the minimum is 'Required/Basic'). Requires administrator.",
    },
    "disable_recall": {
        "name": "Disable Windows Recall (AI)",
        "desc": "Blocks, via policy, Windows Recall, the Copilot+ PC feature that "
                "automatically captures screenshots of your screen to analyze with AI. Requires administrator.",
    },
    "disable_websearch": {
        "name": "Remove web results from search",
        "desc": "Removes internet results from the Windows search box; it only "
                "searches your PC, without sending what you type. Requires administrator.",
    },
    # ----------------------------------- Network --------------------------------
    "qos_bandwidth": {
        "name": "Free up the reserved bandwidth (QoS)",
        "desc": "Allows using the 20% of bandwidth Windows reserves by default for "
                "QoS, leaving the full 100% available for your downloads. Requires administrator.",
    },
    "disable_delivery_opt": {
        "name": "Disable P2P update downloads",
        "desc": "Disables Delivery Optimization: your PC stops sharing (uploading) "
                "Windows updates to other computers over the internet. Requires administrator.",
    },
    "network_throttling": {
        "name": "Disable network throttling (multimedia)",
        "desc": "Removes the ~10 packets/ms limit Windows applies to the network to "
                "reserve CPU for multimedia tasks; useful on fast connections and online games. Requires administrator.",
    },
    "disable_nagle": {
        "name": "Disable Nagle's algorithm (lower latency)",
        "desc": "Makes the network send small packets instantly instead of grouping "
                "them for a few milliseconds to save traffic (Nagle's algorithm). Reduces perceived "
                "latency in online games. Applies to every detected network adapter. Requires administrator and a restart.",
    },
    # ------------------------------------- Gaming ---------------------------------
    "disable_game_dvr": {
        "name": "Disable background recording (Game DVR)",
        "desc": "Disables the Xbox Game Bar's background capture, which consumes CPU "
                "and GPU while you play. You gain some FPS.",
    },
    "hags": {
        "name": "Hardware-accelerated GPU scheduling (HAGS)",
        "desc": "Enables 'hardware-accelerated GPU scheduling': lets the GPU manage "
                "its own memory, which can reduce latency. Requires administrator and a restart.",
    },
    "game_priority": {
        "name": "Optimize system priority for games",
        "desc": "Raises the CPU/GPU priority of games and reduces the system's "
                "reservation for multimedia tasks, prioritizing the active game. Requires administrator.",
    },
    "fso_off": {
        "name": "Disable fullscreen optimizations (FSO)",
        "desc": "Makes fullscreen games use exclusive mode instead of Windows' "
                "'fullscreen optimizations', which usually reduces input lag.",
    },
    "sticky_keys": {
        "name": "Disable the Sticky Keys prompt",
        "desc": "Removes the 'sticky keys' window that pops up when Shift is pressed "
                "5 times in a row and interrupts games in the middle of combat.",
    },
    "vbs_off": {
        "name": "Disable VBS / Memory Integrity (more FPS)",
        "desc": "Disables Virtualization-based Security (VBS/HVCI, 'Memory "
                "Integrity'), which can cost between 5% and 25% FPS. WARNING: REDUCES SECURITY. Requires "
                "administrator and a restart.",
    },
    # -------------------------------------- System ---------------------------------
    "long_paths": {
        "name": "Enable long paths (over 260 characters)",
        "desc": "Lifts the historical 260-character limit on file paths, for "
                "compatible apps and tools (Git, Node, etc.). Requires administrator.",
    },
    "ntfs_lastaccess": {
        "name": "Disable the NTFS 'last access' timestamp",
        "desc": "Stops NTFS from writing the 'last access' date every time a file is "
                "opened, reducing disk writes. Requires administrator.",
    },
    "no_auto_reboot": {
        "name": "Prevent automatic restart after updates",
        "desc": "After installing updates, Windows won't restart on its own while "
                "someone is signed in (avoids losing work). Requires administrator.",
    },
    "uac_quiet": {
        "name": "Reduce UAC prompts (less secure)",
        "desc": "User Account Control (UAC) stops dimming the screen and asking for "
                "confirmation when running tasks as administrator. WARNING: REDUCES SECURITY against "
                "malware. Requires administrator and a restart.",
    },
    "disable_smartscreen": {
        "name": "Disable SmartScreen (less secure)",
        "desc": "Disables the SmartScreen filter that warns when opening uncommon "
                "apps and downloaded files. WARNING: REDUCES SECURITY against malicious downloads. Requires "
                "administrator and a restart.",
    },
    "reserved_storage_off": {
        "name": "Disable reserved storage",
        "desc": "Tells Windows not to reserve ~7 GB of disk space for future updates; "
                "the space is freed after the next feature update. Requires administrator.",
    },
    "disable_sysmain": {
        "name": "Disable the SysMain service (Superfetch)",
        "desc": "Sets the SysMain service (formerly Superfetch), which preloads apps "
                "into RAM, to 'Disabled'. Recommended on SSDs, where it adds little benefit and causes "
                "extra writes. Requires administrator and a restart.",
    },
    # -------------------------------- New tweaks: extra ----------------------------
    "hide_onedrive": {
        "name": "Hide OneDrive from the File Explorer sidebar",
        "desc": "Removes the OneDrive icon from File Explorer's left column (does not "
                "uninstall OneDrive, only hides it from navigation).",
    },
    "hide_gallery": {
        "name": "Hide 'Gallery' in File Explorer",
        "desc": "Removes the 'Gallery' item (the recent photos view) from File "
                "Explorer's left column, if your Windows 11 version includes it.",
    },
    "context_cmd": {
        "name": "Add 'Open Command Prompt here'",
        "desc": "Adds an option to the right-click menu (on a folder's background) to "
                "open Command Prompt directly at that path.",
    },
    "context_pwsh": {
        "name": "Add 'Open PowerShell here'",
        "desc": "Adds an option to the right-click menu (on a folder's background) to "
                "open PowerShell directly located at that path.",
    },
    "widgets_policy": {
        "name": "Disable Widgets completely",
        "desc": "Disables the Widgets feature system-wide via policy (more effective "
                "than just hiding the button): removes the weather and news panel. Requires administrator.",
    },
    "desktop_hide_spotlight": {
        "name": "Hide the Spotlight icon on the desktop",
        "desc": "Removes the 'Learn more about this picture' icon that appears on the "
                "desktop when you use Windows Spotlight as your wallpaper.",
    },
    "power_plan_high": {
        "name": "Power plan: High performance",
        "desc": "Activates Windows' 'High performance' power plan using the powercfg "
                "command (doesn't turn off the screen/disk, prioritizing performance). Turning it off "
                "switches back to 'Balanced'. Requires administrator.",
    },
    "power_throttling": {
        "name": "Disable power throttling",
        "desc": "Prevents Windows from lowering CPU frequency to save power on "
                "background apps. Useful on desktops for maximum performance. Requires administrator and a restart.",
    },
    "background_apps": {
        "name": "Disable background apps",
        "desc": "Prevents Store apps from running in the background (Windows 11 "
                "removed the global switch from Settings). Saves RAM, CPU and battery.",
    },
    "first_logon_anim": {
        "name": "Disable the welcome animation",
        "desc": "Removes the 'Preparing Windows / Hi' animation shown the first time "
                "each user signs in, speeding up that sign-in. Requires administrator.",
    },
    "disable_diagtrack": {
        "name": "Disable the telemetry service (DiagTrack)",
        "desc": "Sets the DiagTrack service ('Connected User Experiences and "
                "Telemetry') to 'Disabled'; it collects and sends usage data to Microsoft. Requires "
                "administrator and a restart.",
    },
    "disable_consumer_features": {
        "name": "Block promoted apps",
        "desc": "Blocks, via policy, the automatic installation of promoted apps and "
                "consumer content (suggestions in Start). May be ignored on Home editions. Requires administrator.",
    },
    "disable_spotlight_features": {
        "name": "Disable Windows Spotlight",
        "desc": "Disables, via policy, every Windows Spotlight feature (rotating "
                "wallpapers, fun facts and suggestions on the lock screen and desktop). Requires administrator.",
    },
}


# ============================================================================
# Traducciones al inglés de los presets.
# ============================================================================
PRESET_EN = {
    "gaming": {
        "name": "Gaming",
        "desc": "Maximum performance for games: priority, hardware GPU scheduling, "
                "network with no extra latency and no telemetry/background tasks stealing resources.",
    },
    "privacy": {
        "name": "Maximum privacy",
        "desc": "Disables telemetry, suggestions, Recall, web search and typing tracking.",
    },
    "minimal": {
        "name": "Minimalist desktop",
        "desc": "Full dark mode and real visual decluttering: no Widgets or search box "
                "on the taskbar, File Explorer and Start menu without suggestions, clean desktop and lock screen.",
    },
    "clean": {
        "name": "Clean & fast",
        "desc": "Removes bloatware and suggestions and speeds up the system without "
                "deeply touching privacy.",
    },
}
