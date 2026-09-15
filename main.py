"""
REPTOSX - Herramienta de personalización y optimización para Windows 11.

Interfaz gráfica moderna (CustomTkinter) para activar/desactivar de forma segura
los ajustes del Registro más habituales para personalizar Windows 11.

Los cambios se aplican en el momento. Los ajustes marcados con un candado
requieren reiniciar la aplicación como administrador.

Idiomas: español (por defecto) e inglés, ver i18n.py.

Creada por reptOSystem  ·  https://www.youtube.com/@reptOSystem
"""
import ctypes
import json
import os
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from tkinter import filedialog

import customtkinter as ctk


def _set_app_user_model_id():
    """Da a REPTOSX su propia identidad de aplicación ante Windows.

    Sin esto, al ejecutarse vía python.exe, la barra de tareas agrupa la
    ventana bajo el icono genérico del intérprete de Python en lugar de
    usar el icono propio de REPTOSX.
    """
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "reptOSystem.REPTOSX.App.1")
    except Exception:
        pass


CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "REPTOSX")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config() -> dict:
    """Carga las preferencias del usuario (tema, idioma, ventana, aviso)."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_config(cfg: dict) -> None:
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def _icon_path():
    """Ruta a REPTOSX.ico, tanto en modo script como empaquetado (.exe)."""
    base = (os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__)))
    ico = os.path.join(base, "REPTOSX.ico")
    return ico if os.path.exists(ico) else None


def apply_icon(window):
    """Aplica el icono de REPTOSX a una ventana (incluido CTkToplevel).

    Se usa iconbitmap(default=...) en la ventana raíz para que TODOS los
    Toplevel hijos (diálogos) hereden el icono automáticamente, además de
    aplicarlo también a la ventana concreta que se pasa.
    """
    ico = _icon_path()
    if not ico:
        return
    try:
        window.iconbitmap(default=ico)
    except Exception:
        try:
            window.iconbitmap(ico)
        except Exception:
            return

    def _reapply():
        # la ventana pudo haberse cerrado/destruido antes de que este
        # temporizador se dispare (p.ej. un diálogo cerrado enseguida)
        try:
            if window.winfo_exists():
                window.iconbitmap(ico)
        except Exception:
            pass

    # CTkToplevel reinicia el icono tras crearse: lo reaplicamos con margen
    window.after(300, _reapply)

import i18n
from registry_utils import is_admin
from tweaks_data import TWEAKS, grouped, first_category, PRESETS, tweak_by_id
import system_info as sysinfo

PRESETS_VIEW = "__presets__"
SYSINFO_VIEW = "__sysinfo__"


def _compute_window_size(screen_w, screen_h):
    """Calcula un tamaño de ventana FIJO como porcentaje de la pantalla real,
    en vez de píxeles absolutos: así se ve bien tanto en portátiles pequeños
    como en monitores 4K, sin desbordar nunca la pantalla.

    El 88% de alto en una pantalla Full HD (1920x1080) es justo lo necesario
    para mostrar toda la barra lateral de categorías sin scroll interno.
    """
    w = max(1000, min(int(screen_w * 0.66), 1450))
    h = max(820, min(int(screen_h * 0.88), 1040))
    w = min(w, screen_w - 60)     # nunca más ancha que la pantalla
    h = min(h, screen_h - 110)    # deja hueco para la barra de tareas y el borde
    return w, h

# Fuente de iconos vectoriales nativa de Windows 11 (nítidos y tintables)
ICON_FONT = "Segoe Fluent Icons"


def _ico(codepoint):
    return chr(codepoint)


# Glifo de Segoe Fluent Icons por categoría (clave interna, ver i18n.py)
CAT_ICON = {
    "appearance": _ico(0xE790),      # paleta
    "taskbar": _ico(0xE990),         # barra
    "start_menu": _ico(0xE80A),      # cuadrícula
    "explorer": _ico(0xE8B7),        # carpeta
    "desktop_icons": _ico(0xE7F8),   # monitor
    "lock_screen": _ico(0xE72E),     # candado
    "performance": _ico(0xE945),     # rayo
    "boot_shutdown": _ico(0xE7E8),   # encendido
    "privacy": _ico(0xEA18),         # escudo
    "network": _ico(0xE774),         # globo
    "gaming": _ico(0xE7FC),          # mando
    "system": _ico(0xE713),          # engranaje
}
ICO_PRESETS = _ico(0xE735)   # estrella
ICO_SYSINFO = _ico(0xEC4E)   # PC de escritorio
ICO_ABOUT = _ico(0xE946)     # info
ICO_RESTORE = _ico(0xE777)   # restaurar (flecha de retorno)
ICO_SEARCH = _ico(0xE721)    # lupa
ICO_WARN = _ico(0xE7BA)      # aviso
ICO_SHIELD = _ico(0xE73A)    # escudo (admin disponible)
ICO_LOCK = _ico(0xE72E)      # candado (admin bloqueado)
ICO_CPU = _ico(0xE950)       # chip / procesador
ICO_RAM = _ico(0xEDA2)       # memoria RAM
ICO_GPU = _ico(0xE964)       # chip / tarjeta gráfica
ICO_DISK = _ico(0xEB05)      # gráfico circular / uso de disco
PRESET_ICON = {
    "gaming": _ico(0xE7FC), "privacy": _ico(0xEA18),
    "minimal": _ico(0xE708), "clean": _ico(0xE945),
}


def clean(text: str) -> str:
    """Quita el selector de variación emoji (U+FE0F) que Tkinter dibuja como
    una caja vacía, provocando un hueco entre el emoji y el texto."""
    return "".join(ch for ch in text if not 0xFE00 <= ord(ch) <= 0xFE0F)


def tweak_matches(tweak, query: str) -> bool:
    q = query.lower()
    return (q in tweak.name.lower()
            or q in tweak.desc.lower()
            or q in i18n.category_label(tweak.category).lower())

# --- Temas: cada uno define una paleta completa y elegante. Clave interna
# estable (no se traduce) -> etiqueta visible en THEME_LABELS. ---
THEMES = {
    "dark": dict(
        appearance="dark",
        ACCENT="#3b82f6", ACCENT_HOVER="#2563eb",
        BG="#0f1116", SIDEBAR_BG="#161922", SURFACE="#1c2029",
        SURFACE_HOVER="#242a35", BORDER="#2b313d",
        TEXT="#e7e9ee", TEXT_MUTED="#969cab", AMBER="#f59e0b"),
    "light": dict(
        appearance="light",
        ACCENT="#2563eb", ACCENT_HOVER="#1d4ed8",
        BG="#f4f5f7", SIDEBAR_BG="#e9ebef", SURFACE="#ffffff",
        SURFACE_HOVER="#eef0f3", BORDER="#d7dbe2",
        TEXT="#1b1e25", TEXT_MUTED="#6b7280", AMBER="#b45309"),
    "cherry_blossom": dict(
        appearance="light",
        ACCENT="#f472b6", ACCENT_HOVER="#ec4899",
        BG="#fff5f9", SIDEBAR_BG="#fbe3ee", SURFACE="#ffffff",
        SURFACE_HOVER="#fdeef5", BORDER="#f6cce0",
        TEXT="#6b2a45", TEXT_MUTED="#b06d89", AMBER="#e26d9a"),
}

THEME_LABELS = {
    "es": {"dark": "Oscuro", "light": "Claro", "cherry_blossom": "Cherry Blossom"},
    "en": {"dark": "Dark", "light": "Light", "cherry_blossom": "Cherry Blossom"},
}

# Variables de paleta actuales (se reasignan al cambiar de tema)
ACCENT = ACCENT_HOVER = BG = SIDEBAR_BG = SURFACE = None
SURFACE_HOVER = BORDER = TEXT = TEXT_MUTED = AMBER = None


def set_palette(pal):
    """Aplica una paleta de THEMES a las variables globales de color."""
    global ACCENT, ACCENT_HOVER, BG, SIDEBAR_BG, SURFACE
    global SURFACE_HOVER, BORDER, TEXT, TEXT_MUTED, AMBER
    ACCENT = pal["ACCENT"]; ACCENT_HOVER = pal["ACCENT_HOVER"]
    BG = pal["BG"]; SIDEBAR_BG = pal["SIDEBAR_BG"]; SURFACE = pal["SURFACE"]
    SURFACE_HOVER = pal["SURFACE_HOVER"]; BORDER = pal["BORDER"]
    TEXT = pal["TEXT"]; TEXT_MUTED = pal["TEXT_MUTED"]; AMBER = pal["AMBER"]


set_palette(THEMES["dark"])

CHANNEL_URL = "https://www.youtube.com/@reptOSystem"


class TweakCard(ctk.CTkFrame):
    """Tarjeta con el nombre, descripción e interruptor de un ajuste."""

    def __init__(self, master, tweak, app, initial_on=None):
        super().__init__(master, corner_radius=12, fg_color=SURFACE,
                         border_width=1, border_color=BORDER)
        self.tweak = tweak
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        self._admin_blocked = tweak.admin and not app.admin

        # título limpio (sin emojis prefijados: así todos quedan alineados)
        self.title_lbl = ctk.CTkLabel(
            self, text=tweak.name, anchor="w", justify="left", text_color=TEXT,
            font=ctk.CTkFont(size=14, weight="bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))

        desc = tweak.desc
        if tweak.restart == "explorer":
            desc += i18n.tr("card.restart_explorer_note")
        elif tweak.restart == "pc":
            desc += i18n.tr("card.restart_pc_note")
        self.desc_lbl = ctk.CTkLabel(
            self, text=desc, anchor="w", justify="left",
            wraplength=540, text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12))
        self.desc_lbl.grid(row=1, column=0, sticky="w", padx=16, pady=(2, 12))

        # badge de indicadores (admin / riesgo) con iconos vectoriales, alineado
        badge = []
        if tweak.danger:
            badge.append(ICO_WARN)
        if tweak.admin:
            badge.append(ICO_LOCK if self._admin_blocked else ICO_SHIELD)
        if badge:
            color = AMBER if tweak.danger else (ACCENT if not self._admin_blocked else TEXT_MUTED)
            ctk.CTkLabel(self, text=" ".join(badge), text_color=color,
                         font=ctk.CTkFont(family=ICON_FONT, size=15)).grid(
                             row=0, column=1, rowspan=2, padx=(0, 8))

        on_state = tweak.is_on() if initial_on is None else initial_on
        self.var = ctk.BooleanVar(value=on_state)
        self.switch = ctk.CTkSwitch(
            self, text="", variable=self.var, width=44,
            progress_color=ACCENT, command=self._on_toggle)
        self.switch.grid(row=0, column=2, rowspan=2, padx=(8, 16), pady=12)

        if self._admin_blocked:
            self.switch.configure(state="disabled")

        # efecto hover suave (sin parpadeo al pasar por el interruptor)
        for w in (self, self.title_lbl, self.desc_lbl):
            w.bind("<Enter>", self._hover_on)
            w.bind("<Leave>", self._hover_off)

    def _hover_on(self, _=None):
        # si la categoría/tema cambió justo mientras el ratón estaba encima,
        # el widget puede haber sido destruido ya: se ignora en ese caso
        try:
            self.configure(fg_color=SURFACE_HOVER)
        except Exception:
            pass

    def _hover_off(self, _=None):
        try:
            x, y = self.winfo_pointerxy()
            w = self.winfo_containing(x, y)
            while w is not None:
                if w == self:
                    return            # el puntero sigue dentro de la tarjeta
                w = getattr(w, "master", None)
            self.configure(fg_color=SURFACE)
        except Exception:
            pass

    def _on_toggle(self):
        if self._admin_blocked:
            self.var.set(self.tweak.is_on())
            self.app.set_status(i18n.tr("status.admin_required"), error=True)
            return
        turn_on = self.var.get()
        # ajustes que reducen la seguridad: pedir confirmación al activar
        if turn_on and self.tweak.danger:
            self.var.set(self.tweak.is_on())   # revertir hasta confirmar
            self.app._confirm(
                i18n.tr("confirm.security_title"),
                i18n.tr("confirm.security_message", name=self.tweak.name),
                lambda: self._do_apply(True))
            return
        self._do_apply(turn_on)

    def _do_apply(self, turn_on):
        try:
            self.tweak.apply(turn_on)
        except PermissionError:
            self.var.set(self.tweak.is_on())
            self.app.set_status(i18n.tr("status.permission_denied"), error=True)
            return
        except OSError as exc:
            self.var.set(self.tweak.is_on())
            self.app.set_status(i18n.tr("status.error_generic", error=exc), error=True)
            return
        except Exception as exc:
            # red de seguridad: cualquier fallo inesperado revierte el interruptor
            # visualmente en vez de dejarlo desincronizado con el estado real
            self.var.set(self.tweak.is_on())
            self.app.set_status(i18n.tr("status.apply_failed", name=self.tweak.name, error=exc), error=True)
            return
        self.var.set(turn_on)
        estado = i18n.tr("status.turned_on") if turn_on else i18n.tr("status.turned_off")
        if self.tweak.restart == "explorer":
            self.app.set_status(i18n.tr("status.tweak_toggled_explorer", name=self.tweak.name, state=estado))
            self.app.mark_needs_restart()
        elif self.tweak.restart == "pc":
            self.app.set_status(i18n.tr("status.tweak_toggled_pc", name=self.tweak.name, state=estado))
        else:
            self.app.set_status(i18n.tr("status.tweak_toggled", name=self.tweak.name, state=estado))
        self.app.refresh_counter()

    def refresh(self):
        self.var.set(self.tweak.is_on())


class NavButton(ctk.CTkFrame):
    """Botón de la barra lateral con icono en una columna de ancho fijo,
    de modo que el texto de todas las entradas queda perfectamente alineado."""

    def __init__(self, master, icon, text, command, bold=False):
        super().__init__(master, fg_color="transparent", corner_radius=8, height=40)
        self.command = command
        self.selected = False
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        self.icon = ctk.CTkLabel(self, text=icon, width=22, text_color=TEXT,
                                 font=ctk.CTkFont(family=ICON_FONT, size=16))
        self.icon.grid(row=0, column=0, padx=(12, 10), pady=8)
        self.lbl = ctk.CTkLabel(self, text=text, anchor="w", text_color=TEXT,
                                font=ctk.CTkFont(size=13,
                                                 weight="bold" if bold else "normal"))
        self.lbl.grid(row=0, column=1, sticky="ew", pady=8, padx=(0, 10))

        for w in (self, self.icon, self.lbl):
            w.bind("<Button-1>", lambda e: self.command())
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
        self.configure(cursor="hand2")

    def _enter(self, _=None):
        try:
            if not self.selected:
                self.configure(fg_color=SURFACE_HOVER)
        except Exception:
            pass

    def _leave(self, _=None):
        try:
            if not self.selected:
                self.configure(fg_color="transparent")
        except Exception:
            pass

    def set_selected(self, sel):
        self.selected = sel
        self.configure(fg_color=ACCENT if sel else "transparent")
        col = "white" if sel else TEXT
        self.lbl.configure(text_color=col)
        self.icon.configure(text_color=col)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.admin = is_admin()
        self.current_cat = first_category()
        self.cards = []
        self._restoring = False

        # preferencias guardadas (tema, idioma, tamaño de ventana, aviso)
        self.cfg = load_config()
        self.theme_name = self.cfg.get("theme") if self.cfg.get("theme") in THEMES else "dark"
        set_palette(THEMES[self.theme_name])
        lang = self.cfg.get("lang")
        i18n.set_lang(lang if lang in i18n.LANGUAGES else "es")

        self.title(i18n.tr("app.title"))
        # tamaño fijo (sin redimensionado): evita el lag de recalcular el
        # layout al arrastrar el borde, y garantiza que la barra lateral se
        # vea completa. El tamaño es un % de la pantalla real (no píxeles
        # absolutos) para que se vea bien en portátiles y en monitores 4K
        # por igual. Solo se conserva la POSICIÓN guardada, no el tamaño.
        win_w, win_h = _compute_window_size(self.winfo_screenwidth(), self.winfo_screenheight())
        geo = self.cfg.get("geometry", "")
        pos = ""
        if isinstance(geo, str) and "+" in geo:
            try:
                x, y = geo.split("+")[1:3]
                pos = f"+{int(x)}+{int(y)}"
            except Exception:
                pos = ""
        self.geometry(f"{win_w}x{win_h}{pos}")
        self.resizable(False, False)
        apply_icon(self)
        ctk.set_appearance_mode(THEMES[self.theme_name]["appearance"])
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_sidebar()
        self._build_topbar()
        self._build_content()
        self._build_statusbar()

        self.show_category(self.current_cat)
        self._style_titlebar()

        # aviso de responsabilidad (salvo que el usuario eligiera no verlo más)
        if not self.cfg.get("skip_disclaimer"):
            self.withdraw()
            self.after(150, self._show_disclaimer)

    def _on_close(self):
        try:
            self.cfg["geometry"] = self.geometry()
            save_config(self.cfg)
        except Exception:
            pass
        self.destroy()

    def report_callback_exception(self, exc, val, tb):
        """Silencia los TclError inofensivos de 'invalid command name' que
        Tkinter/CustomTkinter pueden lanzar si un widget (p.ej. el interruptor
        de una tarjeta) se destruye justo cuando tenía un redibujado pendiente
        en la cola de eventos (ocurre al cambiar de categoría muy rápido). No
        afecta al funcionamiento; cualquier OTRO error se sigue reportando
        con normalidad para poder depurarlo."""
        import tkinter
        if issubclass(exc, tkinter.TclError) and "invalid command name" in str(val):
            return
        super().report_callback_exception(exc, val, tb)

    # ---------- construcción de la interfaz ----------
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=242, corner_radius=0, fg_color=SIDEBAR_BG)
        sb.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sb.grid_propagate(False)

        # --- cabecera con logo de marca ---
        head = ctk.CTkFrame(sb, fg_color="transparent")
        head.pack(fill="x", padx=18, pady=(20, 16))
        badge = ctk.CTkFrame(head, width=42, height=42, corner_radius=12, fg_color=ACCENT)
        badge.pack(side="left")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="R", text_color="white",
                     font=ctk.CTkFont(size=23, weight="bold")).pack(expand=True)
        txt = ctk.CTkFrame(head, fg_color="transparent")
        txt.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(txt, text="REPTOSX", anchor="w", text_color=TEXT,
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(txt, text=i18n.tr("sidebar.tagline"), anchor="w", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11)).pack(anchor="w")

        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x", padx=14, pady=(0, 6))

        # zona inferior (idioma + tema + acerca de) anclada abajo ANTES del área scrollable
        bottom = ctk.CTkFrame(sb, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=10, pady=(6, 14))

        # área de categorías con scroll, agrupada por grupo
        nav = ctk.CTkScrollableFrame(sb, fg_color="transparent")
        nav.pack(side="top", fill="both", expand=True, padx=2)

        self.cat_buttons = {}

        # acceso destacado a los Presets y a la info del equipo
        pbtn = NavButton(nav, ICO_PRESETS, i18n.tr("nav.presets"),
                         lambda: self.show_category(PRESETS_VIEW), bold=True)
        pbtn.pack(fill="x", padx=6, pady=(2, 1))
        self.cat_buttons[PRESETS_VIEW] = pbtn

        sbtn = NavButton(nav, ICO_SYSINFO, i18n.tr("nav.my_pc"),
                         lambda: self.show_category(SYSINFO_VIEW), bold=True)
        sbtn.pack(fill="x", padx=6, pady=(1, 6))
        self.cat_buttons[SYSINFO_VIEW] = sbtn

        for group, cats in grouped():
            ctk.CTkLabel(nav, text=i18n.group_label(group).upper(), anchor="w", text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=11, weight="bold")).pack(
                             fill="x", padx=14, pady=(14, 4))
            for cat in cats:
                btn = NavButton(nav, CAT_ICON.get(cat, ""), i18n.category_label(cat),
                                lambda c=cat: self.show_category(c))
                btn.pack(fill="x", padx=6, pady=1)
                self.cat_buttons[cat] = btn

        # --- inferior: acerca de + tema + idioma ---
        self.restore_point_btn = NavButton(bottom, ICO_RESTORE, i18n.tr("nav.restore_point"),
                                           self.create_restore_point)
        self.restore_point_btn.pack(fill="x", pady=(0, 2))
        self.about_btn = NavButton(bottom, ICO_ABOUT, i18n.tr("nav.about"), self.show_about)
        self.about_btn.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(bottom, text=i18n.tr("sidebar.theme_label"), anchor="w", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=8)
        theme_labels = THEME_LABELS[i18n.get_lang()]
        self.theme_menu = ctk.CTkOptionMenu(
            bottom, values=[theme_labels[k] for k in THEMES.keys()], height=34,
            command=self._on_theme_selected, fg_color=SURFACE, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER, text_color=TEXT)
        self.theme_menu.set(theme_labels[self.theme_name])
        self.theme_menu.pack(fill="x", pady=(6, 10))

        ctk.CTkLabel(bottom, text=i18n.tr("sidebar.lang_label"), anchor="w", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=8)
        self.lang_menu = ctk.CTkOptionMenu(
            bottom, values=[i18n.LANG_NAMES[c] for c in i18n.LANGUAGES], height=34,
            command=self._on_language_selected, fg_color=SURFACE, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER, text_color=TEXT)
        self.lang_menu.set(i18n.LANG_NAMES[i18n.get_lang()])
        self.lang_menu.pack(fill="x", pady=(6, 0))

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=66, corner_radius=0, fg_color=BG)
        bar.grid(row=0, column=1, sticky="nsew")
        bar.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(bar, height=1, fg_color=BORDER).grid(
            row=1, column=0, columnspan=3, sticky="ew")

        self.search = ctk.CTkEntry(
            bar, placeholder_text=i18n.tr("topbar.search_placeholder"), height=40, corner_radius=10,
            fg_color=SURFACE, border_color=BORDER, border_width=1, text_color=TEXT)
        self.search.grid(row=0, column=0, sticky="ew", padx=(22, 10), pady=13)
        self.search.bind("<KeyRelease>", lambda e: self._apply_search())

        self._restart_text = i18n.tr("topbar.restart_explorer")
        self.restart_btn = ctk.CTkButton(
            bar, text=self._restart_text, width=180, height=40, corner_radius=10,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, command=self.restart_explorer)
        self.restart_btn.grid(row=0, column=1, padx=(0, 10), pady=13)

        if not self.admin:
            self.admin_btn = ctk.CTkButton(
                bar, text=clean(i18n.tr("topbar.restart_as_admin")), width=200, height=40,
                corner_radius=10, fg_color="#b45309", hover_color="#92400e",
                command=self.relaunch_as_admin)
            self.admin_btn.grid(row=0, column=2, padx=(0, 22), pady=13)

    def _build_content(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=1, column=1, sticky="ew", padx=24, pady=(12, 0))
        header.grid_columnconfigure(1, weight=1)

        self.title_icon = ctk.CTkLabel(
            header, text="", text_color=ACCENT, width=30,
            font=ctk.CTkFont(family=ICON_FONT, size=22))
        self.title_icon.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.cat_title = ctk.CTkLabel(
            header, text="", anchor="w", text_color=TEXT,
            font=ctk.CTkFont(size=23, weight="bold"))
        self.cat_title.grid(row=0, column=1, sticky="w")

        self.count_lbl = ctk.CTkLabel(
            header, text="", anchor="e", text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12))
        self.count_lbl.grid(row=0, column=2, sticky="e", padx=(8, 14))

        self.only_active = ctk.BooleanVar(value=False)
        self.filter_switch = ctk.CTkSwitch(
            header, text=i18n.tr("content.filter_active_only"), variable=self.only_active,
            progress_color=ACCENT, command=self._render_cards,
            font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.filter_switch.grid(row=0, column=3, sticky="e", padx=(0, 12))

        self.restore_btn = ctk.CTkButton(
            header, text=i18n.tr("content.restore_category"), width=160, height=34, corner_radius=9,
            fg_color="transparent", border_width=1,
            border_color=BORDER, text_color=TEXT_MUTED,
            hover_color=SURFACE_HOVER, command=self._restore_current_category)
        self.restore_btn.grid(row=0, column=4, sticky="e")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=2, column=1, sticky="nsew", padx=18, pady=(10, 0))
        self.scroll.grid_columnconfigure(0, weight=1)

    def _build_statusbar(self):
        wrap = ctk.CTkFrame(self, height=32, corner_radius=0, fg_color=SIDEBAR_BG)
        wrap.grid(row=3, column=1, sticky="nsew")
        wrap.grid_propagate(False)
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x")
        self.status = ctk.CTkLabel(
            wrap, text=self._default_status(), anchor="w",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=12))
        self.status.pack(side="left", fill="x", expand=True, padx=4)

    # ---------- lógica ----------
    def _default_status(self):
        mode = i18n.tr("status.mode_admin") if self.admin else i18n.tr("status.mode_standard")
        return i18n.tr("status.ready", mode=mode, count=len(TWEAKS))

    def show_category(self, cat):
        self.current_cat = cat
        if self.search.get().strip():
            self.search.delete(0, "end")   # salir del modo búsqueda al elegir categoría
        self._highlight(cat)
        self._render_cards()

    def _highlight(self, cat):
        for c, btn in self.cat_buttons.items():
            btn.set_selected(c == cat)

    def _set_controls(self, visible):
        """Muestra u oculta el filtro, el contador y el botón de restaurar."""
        widgets = (self.count_lbl, self.filter_switch, self.restore_btn)
        for w in widgets:
            (w.grid() if visible else w.grid_remove())

    def _update_counter(self, source, states=None):
        if not source:
            self.count_lbl.configure(text="")
            return
        if states is not None:
            active = sum(1 for t in source if states.get(t.id, False))
        else:
            active = sum(1 for t in source if t.is_on())
        self.count_lbl.configure(text=i18n.tr("content.active_count", active=active, total=len(source)))

    def refresh_counter(self):
        """Recalcula el contador de la categoría actual (tras un cambio)."""
        if self.search.get().strip() or self.current_cat == PRESETS_VIEW:
            return
        source = [t for t in TWEAKS if t.category == self.current_cat]
        self._update_counter(source)

    def _render_cards(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self.cards = []
        query = self.search.get().strip()

        # --- Vista de Presets ---
        if not query and self.current_cat == PRESETS_VIEW:
            self.title_icon.configure(text=ICO_PRESETS)
            self.cat_title.configure(text=i18n.tr("presets.title"))
            self._set_controls(visible=False)
            self._update_counter(None)
            self._render_presets()
            return

        # --- Vista de información del equipo ---
        if not query and self.current_cat == SYSINFO_VIEW:
            self.title_icon.configure(text=ICO_SYSINFO)
            self.cat_title.configure(text=i18n.tr("sysinfo.title"))
            self._set_controls(visible=False)
            self._update_counter(None)
            self._render_system_info()
            return

        row = 0
        states = None
        if query:
            self.title_icon.configure(text=ICO_SEARCH)
            self.cat_title.configure(text=i18n.tr("search.results_of", query=query))
            self._highlight(None)
            self._set_controls(visible=False)
            source = TWEAKS                     # búsqueda global
        else:
            self.title_icon.configure(text=CAT_ICON.get(self.current_cat, ""))
            self.cat_title.configure(text=i18n.category_label(self.current_cat))
            self._set_controls(visible=True)
            source = [t for t in TWEAKS if t.category == self.current_cat]
            # se calcula is_on() una sola vez por ajuste (evita, p.ej., lanzar
            # el proceso "powercfg" varias veces al abrir la misma categoría)
            states = {t.id: t.is_on() for t in source}

        only_active = self.only_active.get() and not query
        last_cat = None
        shown = 0
        for tweak in source:
            if query and not tweak_matches(tweak, query):
                continue
            if only_active and not states[tweak.id]:
                continue
            if query and tweak.category != last_cat:
                hdr = ctk.CTkFrame(self.scroll, fg_color="transparent")
                hdr.grid(row=row, column=0, sticky="w", padx=8, pady=(12, 2))
                ctk.CTkLabel(hdr, text=CAT_ICON.get(tweak.category, ""), text_color=ACCENT,
                             font=ctk.CTkFont(family=ICON_FONT, size=14)).pack(side="left", padx=(0, 8))
                ctk.CTkLabel(hdr, text=i18n.category_label(tweak.category), anchor="w", text_color=TEXT_MUTED,
                             font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
                last_cat = tweak.category
                row += 1
            initial_on = states[tweak.id] if states is not None else None
            card = TweakCard(self.scroll, tweak, self, initial_on=initial_on)
            card.grid(row=row, column=0, sticky="ew", padx=4, pady=5)
            self.cards.append(card)
            row += 1
            shown += 1
        if shown == 0:
            msg = i18n.tr("search.no_results") if query else i18n.tr("category.no_active")
            ctk.CTkLabel(self.scroll, text=msg, text_color=TEXT_MUTED).grid(
                row=0, column=0, pady=34)
        self._update_counter(None if query else source, states=states)

    def _render_presets(self):
        ctk.CTkLabel(self.scroll, justify="left", anchor="w", wraplength=640,
                     text_color=TEXT_MUTED, font=ctk.CTkFont(size=12),
                     text=clean(i18n.tr("presets.intro"))).grid(
                         row=0, column=0, sticky="w", padx=10, pady=(0, 12))
        row = 1
        for preset in PRESETS:
            card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color=SURFACE,
                                border_width=1, border_color=BORDER)
            card.grid(row=row, column=0, sticky="ew", padx=4, pady=6)
            card.grid_columnconfigure(0, weight=1)
            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))
            ctk.CTkLabel(hdr, text=PRESET_ICON.get(preset["id"], ""), text_color=ACCENT,
                         font=ctk.CTkFont(family=ICON_FONT, size=18)).pack(side="left", padx=(0, 11))
            ctk.CTkLabel(hdr, text=i18n.preset_name(preset), anchor="w", text_color=TEXT,
                         font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            ctk.CTkLabel(card, text=i18n.preset_desc(preset), anchor="w", justify="left",
                         wraplength=560, text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w",
                                                         padx=16, pady=(2, 10))
            # lista de los ajustes que cambia el preset (con marcas 🔒 admin / ⚠ riesgo)
            names = []
            for tid in preset["set"]:
                t = tweak_by_id(tid)
                if not t:
                    continue
                nm = t.name
                if t.danger:
                    nm = "⚠ " + nm
                if t.admin:
                    nm = "🔒 " + nm
                names.append(nm)
            ctk.CTkLabel(card, text=i18n.tr("presets.changes_count", n=len(names)), anchor="w",
                         text_color=ACCENT, font=ctk.CTkFont(size=11, weight="bold")).grid(
                             row=2, column=0, sticky="w", padx=16, pady=(0, 2))
            ctk.CTkLabel(card, text=clean("  ·  ".join(names)),
                         anchor="w", justify="left", wraplength=560,
                         text_color=TEXT_MUTED, font=ctk.CTkFont(size=11)).grid(
                             row=3, column=0, sticky="w", padx=16, pady=(0, 14))
            ctk.CTkButton(card, text=i18n.tr("presets.apply_button"), width=110, height=36, corner_radius=9,
                          fg_color=ACCENT, hover_color=ACCENT_HOVER,
                          command=lambda p=preset: self.apply_preset(p)).grid(
                              row=0, column=1, rowspan=4, padx=16, pady=12, sticky="n")
            row += 1

        # tu configuración: exportar / importar / restaurar todo
        ctk.CTkFrame(self.scroll, height=1, fg_color=BORDER).grid(
            row=row, column=0, sticky="ew", padx=8, pady=16)
        row += 1
        ctk.CTkLabel(self.scroll, text=i18n.tr("presets.my_config_label"), anchor="w", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11, weight="bold")).grid(
                         row=row, column=0, sticky="w", padx=8, pady=(0, 6))
        row += 1

        profile_bar = ctk.CTkFrame(self.scroll, fg_color="transparent")
        profile_bar.grid(row=row, column=0, sticky="w", padx=4, pady=(0, 10))
        ctk.CTkButton(profile_bar, text=i18n.tr("presets.export_button"),
                      height=38, corner_radius=9, fg_color="transparent", border_width=1,
                      border_color=BORDER, text_color=TEXT, hover_color=SURFACE_HOVER,
                      command=self.export_profile).pack(side="left", padx=(0, 8))
        ctk.CTkButton(profile_bar, text=i18n.tr("presets.import_button"),
                      height=38, corner_radius=9, fg_color="transparent", border_width=1,
                      border_color=BORDER, text_color=TEXT, hover_color=SURFACE_HOVER,
                      command=self.import_profile).pack(side="left")
        row += 1

        ctk.CTkButton(self.scroll, text=i18n.tr("presets.restore_all_button"),
                      height=40, corner_radius=10, fg_color="transparent", border_width=1,
                      border_color="#b91c1c", text_color="#ef4444",
                      hover_color=SURFACE_HOVER,
                      command=self._restore_all).grid(row=row, column=0, sticky="w", padx=4)

    def _render_system_info(self):
        ctk.CTkLabel(self.scroll, justify="left", anchor="w", wraplength=680,
                     text_color=TEXT_MUTED, font=ctk.CTkFont(size=12),
                     text=i18n.tr("sysinfo.intro")).grid(
                         row=0, column=0, sticky="w", padx=10, pady=(0, 12))
        row = 1

        def simple_card(icon, title, subtitle):
            nonlocal row
            card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color=SURFACE,
                                border_width=1, border_color=BORDER)
            card.grid(row=row, column=0, sticky="ew", padx=4, pady=5)
            card.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(card, text=icon, text_color=ACCENT, width=44,
                         font=ctk.CTkFont(family=ICON_FONT, size=22)).grid(
                             row=0, column=0, rowspan=2, padx=(16, 4), pady=16)
            ctk.CTkLabel(card, text=title, anchor="w", text_color=TEXT,
                         font=ctk.CTkFont(size=14, weight="bold")).grid(
                             row=0, column=1, sticky="w", padx=(6, 16), pady=(16, 0))
            ctk.CTkLabel(card, text=subtitle, anchor="w", justify="left", wraplength=700,
                         text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).grid(
                             row=1, column=1, sticky="w", padx=(6, 16), pady=(0, 16))
            row += 1

        def gauge_card(icon, title, bar_fraction, footer_text):
            nonlocal row
            card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color=SURFACE,
                                border_width=1, border_color=BORDER)
            card.grid(row=row, column=0, sticky="ew", padx=4, pady=5)
            card.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(card, text=icon, text_color=ACCENT, width=44,
                         font=ctk.CTkFont(family=ICON_FONT, size=22)).grid(
                             row=0, column=0, rowspan=3, padx=(16, 4), pady=16)
            ctk.CTkLabel(card, text=title, anchor="w", text_color=TEXT,
                         font=ctk.CTkFont(size=14, weight="bold")).grid(
                             row=0, column=1, sticky="w", padx=(6, 16), pady=(16, 4))
            bar = ctk.CTkProgressBar(card, progress_color=ACCENT, fg_color=BORDER, height=10)
            bar.set(max(0.0, min(1.0, bar_fraction)))
            bar.grid(row=1, column=1, sticky="ew", padx=(6, 16), pady=(0, 6))
            ctk.CTkLabel(card, text=footer_text, anchor="w",
                         text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).grid(
                             row=2, column=1, sticky="w", padx=(6, 16), pady=(0, 16))
            row += 1

        # --- CPU ---
        cpu = sysinfo.cpu_info()
        simple_card(ICO_CPU, i18n.tr("sysinfo.cpu_title"),
                   i18n.tr("sysinfo.cpu_threads", name=cpu["name"], threads=cpu["threads"]))

        # --- RAM ---
        ram = sysinfo.ram_info()
        gauge_card(ICO_RAM, i18n.tr("sysinfo.ram_title"), ram["percent"] / 100,
                  i18n.tr("sysinfo.ram_usage", used=ram["used_gb"], total=ram["total_gb"],
                         percent=ram["percent"]))

        # --- GPU(s) ---
        for g in sysinfo.gpu_info():
            vram_txt = i18n.tr("sysinfo.gpu_vram", vram=g["vram_gb"]) if g.get("vram_gb") else ""
            simple_card(ICO_GPU, i18n.tr("sysinfo.gpu_title"), f"{g['name']}{vram_txt}")

        # --- Discos (espacio) ---
        for d in sysinfo.disks_info():
            used_pct = (d["used_gb"] / d["total_gb"]) if d["total_gb"] else 0
            gauge_card(ICO_DISK, i18n.tr("sysinfo.disk_title", letter=d["letter"]), used_pct,
                      i18n.tr("sysinfo.disk_usage", free=d["free_gb"], total=d["total_gb"]))

        # --- Windows ---
        win = sysinfo.windows_version()
        win_desc = win["product"]
        if win["display_version"]:
            win_desc += i18n.tr("sysinfo.os_version", version=win["display_version"])
        win_desc += f"  ·  build {win['build']}  ·  {win['arch']}"
        simple_card(ICO_SYSINFO, i18n.tr("sysinfo.os_title"), win_desc)

        # --- tipo de disco (SSD/HDD): tarda un par de segundos, se calcula
        # en segundo plano para no congelar la interfaz al abrir esta página ---
        ctk.CTkLabel(self.scroll, text=i18n.tr("sysinfo.disks_physical_label"), anchor="w",
                     text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11, weight="bold")).grid(
                         row=row, column=0, sticky="w", padx=8, pady=(14, 4))
        row += 1
        media_lbl = ctk.CTkLabel(self.scroll, text=i18n.tr("sysinfo.detecting_disk_type"),
                                 anchor="w", justify="left", wraplength=700,
                                 text_color=TEXT_MUTED, font=ctk.CTkFont(size=12))
        media_lbl.grid(row=row, column=0, sticky="w", padx=10, pady=(0, 10))
        row += 1

        def worker():
            media = sysinfo.disk_media_types()

            def apply_result():
                # la vista pudo haber cambiado (o cerrado la app) mientras
                # PowerShell terminaba de consultar los discos
                try:
                    if not media_lbl.winfo_exists():
                        return
                    if media:
                        text = "  ·  ".join(f"{m['name']} ({m['media']})" for m in media)
                    else:
                        text = i18n.tr("sysinfo.disk_type_unavailable")
                    media_lbl.configure(text=text)
                except Exception:
                    pass
            try:
                # si se cerró la app entera mientras PowerShell consultaba
                # los discos, self.after() en sí mismo puede fallar
                self.after(0, apply_result)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _apply_search(self):
        self._render_cards()

    # ---------- aviso de responsabilidad ----------
    def _show_disclaimer(self):
        dlg = ctk.CTkToplevel(self, fg_color=BG)
        self._disclaimer = dlg
        dlg.title(i18n.tr("disclaimer.title_bar"))
        dlg.geometry("580x540")
        dlg.resizable(False, False)
        apply_icon(dlg)
        dlg.protocol("WM_DELETE_WINDOW", self._decline_disclaimer)

        # centrar en pantalla
        dlg.update_idletasks()
        sw, sh = dlg.winfo_screenwidth(), dlg.winfo_screenheight()
        x, y = (sw - 580) // 2, (sh - 540) // 2
        dlg.geometry(f"580x540+{x}+{y}")
        dlg.after(150, dlg.grab_set)

        head = ctk.CTkFrame(dlg, fg_color="transparent")
        head.pack(anchor="w", padx=26, pady=(22, 2))
        ctk.CTkLabel(head, text=ICO_WARN, text_color=AMBER,
                     font=ctk.CTkFont(family=ICON_FONT, size=24)).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(head, text=i18n.tr("disclaimer.header"), text_color=TEXT,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkLabel(dlg, text=i18n.tr("disclaimer.subtitle"),
                     text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=26, pady=(0, 14))

        ctk.CTkLabel(dlg, text=clean(i18n.tr("disclaimer.body")), justify="left", anchor="w",
                     wraplength=520, text_color=TEXT,
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=26)

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(side="bottom", fill="x", padx=26, pady=20)

        self._skip_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(btns, text=i18n.tr("disclaimer.checkbox"),
                        variable=self._skip_var, checkbox_width=20, checkbox_height=20,
                        fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).pack(
                            side="left")
        ctk.CTkButton(btns, text=i18n.tr("disclaimer.exit_button"), width=110, height=40,
                      fg_color="transparent", border_width=1,
                      border_color=BORDER, text_color=TEXT_MUTED,
                      hover_color=SURFACE_HOVER,
                      command=self._decline_disclaimer).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btns, text=i18n.tr("disclaimer.accept_button"), width=180, height=40,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._accept_disclaimer).pack(side="right")

    def _accept_disclaimer(self):
        if getattr(self, "_skip_var", None) is not None and self._skip_var.get():
            self.cfg["skip_disclaimer"] = True
            save_config(self.cfg)
        try:
            self._disclaimer.grab_release()
            self._disclaimer.destroy()
        except Exception:
            pass
        self.deiconify()
        self.lift()
        self.focus_force()
        self.after(50, self._style_titlebar)
        # reaplicar el icono ahora que la ventana es visible: si se aplicó
        # mientras estaba withdraw()n, el icono de la barra de tareas podía
        # no quedar bien registrado por Windows
        self.after(50, lambda: apply_icon(self))

    def _decline_disclaimer(self):
        self.destroy()

    # ---------- presets y restauración ----------
    def apply_preset(self, preset):
        self._confirm_bulk_apply(
            preset["set"].items(),
            dialog_title=i18n.tr("confirm.apply_preset_title", name=i18n.preset_name(preset)),
            status_title=i18n.preset_name(preset))

    def _restore_current_category(self):
        cat = self.current_cat
        cat_label = i18n.category_label(cat)
        targets = [(t.id, False) for t in TWEAKS if t.category == cat]
        self._confirm_bulk_apply(
            targets, dialog_title=i18n.tr("confirm.restore_category_title"),
            status_title=i18n.tr("confirm.restore_category_status", cat=cat_label),
            note=i18n.tr("confirm.restore_category_note", cat=cat_label))

    def _restore_all(self):
        targets = [(t.id, False) for t in TWEAKS]
        self._confirm_bulk_apply(
            targets, dialog_title=i18n.tr("confirm.restore_all_title"),
            status_title=i18n.tr("confirm.restore_all_status"),
            note=i18n.tr("confirm.restore_all_note"))

    def _confirm_bulk_apply(self, items, dialog_title, status_title, note=None):
        """Punto de entrada único para aplicar varios ajustes a la vez
        (presets, restaurar categoría/todo, importar un perfil). Antes de
        tocar nada: calcula cuántos ajustes cambiarían de verdad, avisa si
        alguno de ellos reduce la seguridad de Windows, y sugiere crear un
        punto de restauración si son muchos cambios."""
        items = list(items)
        changes = []
        danger_names = []
        for tid, state in items:
            t = tweak_by_id(tid)
            if t is None:
                continue
            if t.is_on() != state:
                changes.append((tid, state))
                if state and t.danger:
                    danger_names.append(t.name)
        if not changes:
            self.set_status(i18n.tr("bulk.no_changes", title=status_title))
            return

        msg = i18n.tr("bulk.will_change", n=len(changes), plural="s" if len(changes) != 1 else "")
        if note:
            msg += "\n\n" + note
        if danger_names:
            msg += i18n.tr("bulk.danger_warning", names=", ".join(danger_names))
        if len(changes) >= 5:
            msg += i18n.tr("bulk.suggest_restore_point")
        self._confirm(dialog_title, msg,
                      lambda: self._apply_bulk(changes, titulo=status_title),
                      confirm_text=i18n.tr("presets.apply_button"))

    def _apply_bulk(self, items, titulo):
        applied = skipped = 0
        need_explorer = need_pc = False
        for tid, state in items:
            t = tweak_by_id(tid)
            if t is None:
                continue
            if t.admin and not self.admin:
                skipped += 1
                continue
            try:
                t.apply(state)
                applied += 1
                if t.restart == "explorer":
                    need_explorer = True
                elif t.restart == "pc":
                    need_pc = True
            except Exception:
                skipped += 1
        if need_explorer:
            self.mark_needs_restart()
        msg = i18n.tr("bulk.applied", title=titulo, n=applied)
        if skipped:
            msg += i18n.tr("bulk.skipped_admin", n=skipped)
        if need_pc:
            msg += i18n.tr("bulk.restart_pc_needed")
        self.set_status(msg)
        self._render_cards()   # refresca el estado de los interruptores

    # ---------- exportar / importar perfil ----------
    def export_profile(self):
        path = filedialog.asksaveasfilename(
            parent=self, title=i18n.tr("export.dialog_title"),
            defaultextension=".json",
            filetypes=[(i18n.tr("export.file_type_label"), "*.json")],
            initialfile="reptosx_perfil.json")
        if not path:
            return
        data = {
            "app": "REPTOSX",
            "format_version": 1,
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "tweaks": {t.id: t.is_on() for t in TWEAKS},
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.set_status(i18n.tr("export.status_success", filename=os.path.basename(path)))
        except Exception as exc:
            self.set_status(i18n.tr("export.status_error", error=exc), error=True)

    def import_profile(self):
        path = filedialog.askopenfilename(
            parent=self, title=i18n.tr("import.dialog_title"),
            filetypes=[(i18n.tr("export.file_type_label"), "*.json"),
                      (i18n.tr("import.all_files_label"), "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            self.set_status(i18n.tr("import.read_error", error=exc), error=True)
            return

        tweaks_field = data.get("tweaks") if isinstance(data, dict) else None
        if not isinstance(tweaks_field, dict):
            self.set_status(i18n.tr("import.invalid_format"), error=True)
            return

        valid_ids = {t.id for t in TWEAKS}
        items, unknown = [], 0
        for tid, state in tweaks_field.items():
            if tid not in valid_ids:
                unknown += 1
                continue
            items.append((tid, bool(state)))
        if not items:
            self.set_status(i18n.tr("import.no_recognized"), error=True)
            return

        fname = os.path.basename(path)
        note = i18n.tr("import.note", filename=fname, n=len(items))
        if unknown:
            note += i18n.tr("import.unknown_note", n=unknown)
        self._confirm_bulk_apply(
            items, dialog_title=i18n.tr("import.confirm_title"),
            status_title=i18n.tr("import.status_title", filename=fname), note=note)

    def _confirm(self, title, message, on_yes, confirm_text=None,
                 confirm_color="#b91c1c", confirm_hover="#991b1b"):
        # evita apilar varios diálogos si se hace doble clic muy rápido
        existing = getattr(self, "_confirm_win", None)
        if existing is not None and existing.winfo_exists():
            existing.focus()
            existing.lift()
            return
        if confirm_text is None:
            confirm_text = i18n.tr("confirm.default_button")
        win = ctk.CTkToplevel(self, fg_color=BG)
        self._confirm_win = win
        win.title(title)
        win.resizable(False, False)
        win.transient(self)
        apply_icon(win)
        win.after(120, win.grab_set)
        ctk.CTkLabel(win, text=title, text_color=TEXT,
                     font=ctk.CTkFont(size=18, weight="bold")).pack(
            anchor="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(win, text=message, justify="left", anchor="w", wraplength=414,
                     text_color=TEXT_MUTED).pack(anchor="w", padx=22)
        btns = ctk.CTkFrame(win, fg_color="transparent")
        btns.pack(side="bottom", fill="x", padx=22, pady=18)
        ctk.CTkButton(btns, text=i18n.tr("confirm.cancel_button"), height=36, corner_radius=9,
                      fg_color="transparent", border_width=1,
                      border_color=BORDER, text_color=TEXT_MUTED,
                      hover_color=SURFACE_HOVER,
                      command=win.destroy).pack(side="right", padx=(8, 0))

        def _go():
            win.destroy()
            on_yes()
        ctk.CTkButton(btns, text=confirm_text, height=36, corner_radius=9,
                      fg_color=confirm_color, hover_color=confirm_hover,
                      command=_go).pack(side="right")

        # altura automática según el contenido real (los mensajes de aplicar
        # presets/importar perfil pueden ser bastante más largos que un
        # simple "restaurar categoría"), con límites razonables
        win.update_idletasks()
        h = max(210, min(win.winfo_reqheight(), 560))
        win.geometry(f"460x{h}")

    def _on_theme_selected(self, label):
        lang = i18n.get_lang()
        labels = THEME_LABELS[lang]
        key = next((k for k, v in labels.items() if v == label), None)
        if key:
            self.apply_theme(key)

    def apply_theme(self, name):
        """Cambia de tema reconstruyendo la interfaz con la nueva paleta."""
        if name not in THEMES:
            return
        self.theme_name = name
        self.cfg["theme"] = name
        save_config(self.cfg)
        set_palette(THEMES[name])
        ctk.set_appearance_mode(THEMES[name]["appearance"])
        self.configure(fg_color=BG)
        self._rebuild_ui()
        self.set_status(i18n.tr("theme.apply_status", name=THEME_LABELS[i18n.get_lang()][name]))

    def _on_language_selected(self, label):
        code = next((c for c in i18n.LANGUAGES if i18n.LANG_NAMES[c] == label), None)
        if code:
            self.apply_language(code)

    def apply_language(self, code):
        """Cambia el idioma de toda la interfaz reconstruyéndola (como el tema)."""
        if code not in i18n.LANGUAGES:
            return
        i18n.set_lang(code)
        self.cfg["lang"] = code
        save_config(self.cfg)
        self.title(i18n.tr("app.title"))
        self._rebuild_ui()
        self.set_status(i18n.tr("lang.apply_status", name=i18n.LANG_NAMES[code]))

    def _rebuild_ui(self):
        """Reconstruye los paneles principales (usado al cambiar tema o idioma)."""
        # cierra diálogos secundarios abiertos: quedarían con los textos/colores del estado anterior
        for attr in ("_about_win", "_confirm_win"):
            win = getattr(self, attr, None)
            if win is not None and win.winfo_exists():
                win.destroy()
        for w in self.grid_slaves():
            w.destroy()
        self._build_sidebar()
        self._build_topbar()
        self._build_content()
        self._build_statusbar()
        self.show_category(self.current_cat)
        self._style_titlebar()

    def _style_titlebar(self):
        """Tinta la barra de título nativa de Windows 11 con los colores del tema."""
        try:
            from ctypes import windll, byref, c_int
            hwnd = windll.user32.GetParent(self.winfo_id())
            pal = THEMES[self.theme_name]

            def cref(h):
                h = h.lstrip("#")
                r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                return c_int(r | (g << 8) | (b << 16))

            dwm = windll.dwmapi
            dark = c_int(1 if pal["appearance"] == "dark" else 0)
            dwm.DwmSetWindowAttribute(hwnd, 20, byref(dark), 4)            # modo oscuro
            dwm.DwmSetWindowAttribute(hwnd, 35, byref(cref(pal["BG"])), 4)   # color barra
            dwm.DwmSetWindowAttribute(hwnd, 36, byref(cref(pal["TEXT"])), 4)  # color texto
        except Exception:
            pass

    def set_status(self, text, error=False):
        self.status.configure(text="  " + text,
                              text_color="#ef4444" if error else TEXT_MUTED)

    def mark_needs_restart(self):
        self.restart_btn.configure(fg_color="#16a34a", hover_color="#15803d",
                                   text=i18n.tr("topbar.restart_explorer_pending"))

    def restart_explorer(self):
        try:
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"],
                           capture_output=True)
            subprocess.Popen("explorer.exe")
            self.restart_btn.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                       text=i18n.tr("topbar.restart_explorer"))
            self.set_status(i18n.tr("explorer.restarted_status"))
        except Exception as exc:
            self.set_status(i18n.tr("explorer.restart_error", error=exc), error=True)

    # ---------- punto de restauración ----------
    def create_restore_point(self):
        if not self.admin:
            self.set_status(i18n.tr("restore_point.admin_required"), error=True)
            return
        if self._restoring:
            self.set_status(i18n.tr("restore_point.already_running"))
            return
        self._confirm(
            i18n.tr("restore_point.confirm_title"),
            i18n.tr("restore_point.confirm_message"),
            self._do_restore_point)

    def _do_restore_point(self):
        self._restoring = True
        self.set_status(i18n.tr("restore_point.creating_status"))

        def worker():
            cmd = ["powershell", "-NoProfile", "-Command",
                   "Checkpoint-Computer -Description 'REPTOSX' "
                   "-RestorePointType 'MODIFY_SETTINGS'"]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True,
                                   creationflags=0x08000000, timeout=180)
                if r.returncode == 0 and not r.stderr.strip():
                    msg, err = i18n.tr("restore_point.success"), False
                else:
                    detail = (r.stderr or r.stdout).strip().splitlines()
                    detail = detail[0] if detail else "unknown error"
                    if "1440" in detail or "frecuencia" in detail.lower() or "frequently" in detail.lower():
                        detail = i18n.tr("restore_point.frequency_error")
                    msg, err = i18n.tr("restore_point.generic_error", detail=detail), True
            except Exception as exc:
                msg, err = i18n.tr("restore_point.generic_error", detail=exc), True
            try:
                # si se cerró la app entera mientras se creaba el punto de
                # restauración, self.after() en sí mismo puede fallar
                self.after(0, lambda: (setattr(self, "_restoring", False),
                                       self.set_status(msg, error=err)))
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def open_channel(self):
        webbrowser.open(CHANNEL_URL)
        self.set_status(i18n.tr("channel.opening_status"))

    def show_about(self):
        if getattr(self, "_about_win", None) is not None and self._about_win.winfo_exists():
            self._about_win.focus()
            return

        win = ctk.CTkToplevel(self, fg_color=BG)
        self._about_win = win
        win.title(i18n.tr("about.title_bar"))
        win.geometry("520x560")
        win.resizable(False, False)
        win.transient(self)
        apply_icon(win)
        win.after(120, win.grab_set)   # modal tras renderizar (evita parpadeo en Windows)

        cont = ctk.CTkScrollableFrame(win, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=24, pady=20)

        head = ctk.CTkFrame(cont, fg_color="transparent")
        head.pack(anchor="w", pady=(0, 4))
        logo = ctk.CTkFrame(head, width=52, height=52, corner_radius=14, fg_color=ACCENT)
        logo.pack(side="left", padx=(0, 14))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="R", text_color="white",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(expand=True)
        ctk.CTkLabel(head, text="REPTOSX", text_color=TEXT,
                     font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        ctk.CTkLabel(cont, text=i18n.tr("about.subtitle"),
                     text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(cont, text=i18n.tr("about.description"), justify="left", anchor="w", text_color=TEXT,
                     wraplength=440, font=ctk.CTkFont(size=13)).pack(anchor="w")

        ctk.CTkFrame(cont, height=1, fg_color=BORDER).pack(fill="x", pady=18)

        ctk.CTkLabel(cont, text=i18n.tr("about.channel_label"), text_color=TEXT,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(cont, text="@reptOSystem",
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(cont, text=clean(i18n.tr("about.visit_button")),
                      height=44, fg_color="#cc0000", hover_color="#990000",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.open_channel).pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(cont, text=CHANNEL_URL,
                     text_color=ACCENT, font=ctk.CTkFont(size=12)).pack(anchor="w")

        ctk.CTkLabel(cont, text=clean(i18n.tr("about.version_footer")),
                     text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(18, 0))

    def relaunch_as_admin(self):
        try:
            if getattr(sys, "frozen", False):
                # ejecutable empaquetado (.exe): relanzar el propio exe
                exe = sys.executable
                params = ""
                workdir = os.path.dirname(exe)
            else:
                exe = sys.executable
                script = os.path.abspath(__file__)
                extra_args = sys.argv[1:]
                params = " ".join(f'"{a}"' for a in [script, *extra_args])
                workdir = os.path.dirname(script)
            # se fija lpDirectory explícitamente: sin esto, un proceso elevado
            # por UAC puede arrancar con el directorio de trabajo en System32
            # y fallar al no encontrar main.py con una ruta relativa
            ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, workdir, 1)
            self.destroy()
        except Exception as exc:
            self.set_status(i18n.tr("elevate.error", error=exc), error=True)


if __name__ == "__main__":
    _set_app_user_model_id()
    App().mainloop()
