# REPTOSX 🛠️

[Español](README.md) · **English**

All-in-one customization and optimization tool for Windows 11. Turn on or off,
from a graphical interface, the Registry tweaks you would normally have to
change by hand in `regedit`.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![UI](https://img.shields.io/badge/UI-CustomTkinter-2563eb)

Created by reptOSystem · Windows customization and optimization channel:
<https://www.youtube.com/@reptOSystem>

## Download

1. Go to the [Releases](https://github.com/ReptOSystem/REPTOSX/releases) section of this repository.
2. Download `REPTOSX.exe` from the latest version.
3. Double-click it.

No Python or anything else to install. Windows will ask for administrator
permission (UAC) when it opens: that is needed to apply the tweaks marked with
the lock icon 🔒. If SmartScreen warns about an "unknown publisher", that is
normal for a new app without a digital signature — choose "More info → Run
anyway".

The app starts in Spanish. You can switch to English from the language
selector on the first screen, or later at the bottom of the sidebar.

## Presets

The Presets section applies several tweaks at once with a single click:

- **🎮 Gaming**: foreground app priority, hardware GPU scheduling, network
  without extra latency, and no telemetry or background tasks taking resources.
- **🔒 Maximum privacy**: telemetry, suggestions, Windows Recall, web search
  and typing data collection reduced to the minimum.
- **🌙 Minimalist desktop**: full dark mode and a much cleaner interface,
  without widgets, suggestions or unnecessary shortcuts.
- **🧹 Clean & fast**: removes bloatware and suggestions, without going deep
  into privacy settings.

Before applying a preset, or restoring a whole category, the app shows how
many tweaks will change and warns if any of them reduces system security.
Each category also has a button to restore only its own tweaks to their
default values.

You can also save your current configuration as **your own preset** with any
name you like; it will appear next to the others so you can apply it again
with one click.

## Export and import configuration

From the Presets section you can export the active configuration to a `.json`
file and import it again later (after reinstalling Windows, for example, or
to share a recommended setup).

## Startup apps

The Startup apps section lists the programs that open by themselves when you
sign in and lets you turn them on or off. It uses the same mechanism as Task
Manager, so nothing is deleted and the change is reversible. Store apps and
scheduled tasks are not included.

## PC information

The My PC section shows the processor, RAM in use, graphics card with its
VRAM, drive space and type (SSD or HDD) and the installed Windows version.
Everything is read locally; nothing is sent anywhere.

## Other features

- Three visual themes — Dark, Light and 🌸 Cherry Blossom — with the
  interface available in Spanish and English.
- Window sized in proportion to the screen, so it looks right on small
  laptops and large monitors alike.
- One-click system restore point.
- A note on every tweak that would have no effect on your Windows version or
  edition (for example, those that need 23H2 or 24H2).
- A notice when a new REPTOSX version is available. It only checks the
  version number on GitHub and can be turned off from About.
- Search tweaks by name or description (Ctrl+F).

## Tweak catalog

The catalog includes 83 tweaks, prioritizing those that are not easily
available from Windows Settings itself.

### Personalization

| Category | Examples |
|---|---|
| Appearance | Dark mode for apps/system, maximum wallpaper quality, disable Aero Shake |
| Taskbar | Align left, hide Task View or search, never combine buttons, show all tray icons |
| Start Menu | Remove Bing, more pinned apps, hide recent items, disable Copilot |
| File Explorer | Show extensions and hidden files, classic context menu, open CMD/PowerShell in the current folder |
| Desktop & Icons | Show or hide This PC, Network, Control Panel and Recycle Bin |
| Lock Screen | Remove ads and trivia, disable the lock screen* |

### Optimization

| Category | Examples |
|---|---|
| Performance | High performance power plan*, no animations, no mouse acceleration |
| Startup & Shutdown | Fast Startup*, hibernation*, startup sound and welcome animation* |
| Privacy & Telemetry | Telemetry*, Windows Recall, web search*, DiagTrack service* |
| Network | Reserved bandwidth (QoS)*, P2P downloads*, Nagle's algorithm* |
| Gaming | Game DVR, hardware GPU scheduling*, system priority* |
| System | Long paths*, SysMain service*, reserved storage*, reduce UAC* |

\* Requires running the app as administrator.

Tweaks that reduce system security are marked in the interface and ask for
confirmation before being enabled. Some changes need File Explorer or the PC
to be restarted to take full effect.

## How it works

Changes are applied immediately when you flip a switch, and each switch
reflects the real state read from the Registry. Turning a tweak off returns it
to the Windows default value.

## Notice ⚠️

REPTOSX modifies the Windows Registry. Every tweak can be reverted from the
app itself, but it is a good idea to create a restore point before applying
several changes at once, especially in the System category.
