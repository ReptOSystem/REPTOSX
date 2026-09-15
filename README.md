# REPTOSX 🛠️ — Herramienta para Windows 11

Personalizador y optimizador **todo-en-uno** del Registro de Windows 11 con
interfaz gráfica moderna. Activa o desactiva con un interruptor los ajustes más
habituales que la gente modifica a mano en el Editor del Registro, sin tocar
`regedit`.

![tema oscuro](https://img.shields.io/badge/UI-CustomTkinter-2563eb) ![Windows](https://img.shields.io/badge/Windows-11-blue) ![YouTube](https://img.shields.io/badge/YouTube-@reptOSystem-cc0000)

> Creada por **reptOSystem** · Canal de personalización y optimización de Windows: <https://www.youtube.com/@reptOSystem>
> (También dentro de la app, en **ℹ️ Acerca de REPTOSX**.)

## Cómo abrirlo

- **Doble clic en `REPTOSX.bat`** — modo normal (ajustes de usuario).
- **Doble clic en `REPTOSX-Admin.bat`** — pide permiso de administrador para
  poder aplicar también los ajustes del sistema (los del candado 🔒).

También puedes ejecutarlo desde una terminal:

```powershell
python main.py
```

## Requisitos

- Windows 11
- Python 3.10+
- `customtkinter` (ya instalado). Si falta: `pip install customtkinter`

## Presets (un clic)

En la sección **⭐ Presets** (arriba en la barra lateral) puedes aplicar varios
ajustes a la vez:

- **🎮 Gaming** — prioridad a primer plano, GPU por hardware, red sin latencia extra (Nagle, QoS), sin telemetría ni tareas de fondo que roben recursos.
- **🔒 Privacidad máxima** — telemetría, sugerencias, Windows Recall (IA), búsqueda web, DiagTrack y rastreo de escritura al mínimo.
- **🌙 Escritorio minimalista** — modo oscuro total y limpieza visual real: sin Widgets ni buscador en la barra, Explorador y menú Inicio sin sugerencias, escritorio y bloqueo limpios.
- **🧹 Limpio y rápido** — quita bloatware y sugerencias y acelera el sistema.

Antes de aplicar un preset (o restaurar una categoría/todo) la app **siempre
pide confirmación**, mostrando cuántos ajustes cambiarán de verdad y avisando
si alguno reduce la seguridad de Windows.

Además, en cada categoría hay un botón **↩ Restaurar categoría**, un filtro
**Solo activados** con contador, y en Presets un **↩ Restaurar TODO a los valores
predeterminados**. Todo es reversible.

## Exportar / importar tu configuración

Desde la sección **⭐ Presets** puedes:

- **Exportar mi configuración** — guarda en un `.json` qué ajustes tienes
  activados ahora mismo. Útil como copia de seguridad o para reinstalar
  Windows sin tener que volver a configurar REPTOSX ajuste a ajuste.
- **Importar configuración** — carga un `.json` exportado antes (el tuyo o
  el de otra persona) y aplícalo con un clic. Ideal para compartir tu
  configuración recomendada con tu comunidad.

## Mi equipo

Sección **🖥️ Mi equipo** en la barra lateral: muestra procesador, memoria RAM
(con barra de uso), tarjeta(s) gráfica(s) con su VRAM, discos (espacio libre
y tipo SSD/HDD) y la versión/build exacta de Windows. Todo se lee localmente
con la API de Windows y el Registro — nada se envía a ningún sitio.

## Funciones de la app

- **3 temas** (Oscuro, Claro y 🌸 Cherry Blossom) con iconos vectoriales nativos
  de Windows 11. La app **recuerda tu tema** entre sesiones.
- **Ventana de tamaño fijo y proporcional** a tu pantalla (no absoluto en
  píxeles): se ve bien tanto en portátiles pequeños como en monitores 4K, y
  siempre cabe toda la barra lateral sin necesidad de scroll.
- **Punto de restauración del sistema con un clic** desde la barra lateral
  (requiere administrador).
- Aviso de responsabilidad al abrir, con opción de **"No volver a mostrar"**.
- Búsqueda global y barra de título nativa tintada con el color del tema.

## Qué incluye (83 ajustes en 2 grupos)

> Catálogo **curado**: se prioriza lo que **no se puede hacer fácilmente desde
> Configuración de Windows** (ajustes de registro, políticas y servicios). Cada
> ajuste reversible ha sido verificado con una prueba de escritura/lectura.

### 🎨 Personalización

| Categoría | Ejemplos |
|-----------|----------|
| Apariencia | Modo oscuro apps/sistema, calidad máxima del fondo de pantalla, desactivar Aero Shake |
| Barra de tareas | Alinear a la izquierda, desactivar Widgets*, ocultar Vista de tareas/búsqueda, **nunca combinar botones**, **mostrar todos los iconos de la bandeja**, "Finalizar tarea" |
| Menú Inicio | Quitar Bing, más anclajes, no mostrar recientes, desactivar Copilot, notificaciones de cuenta |
| Explorador | Mostrar extensiones/ocultos, **menú contextual clásico**, ocultar OneDrive/Galería, **"Abrir CMD/PowerShell aquí"**, abrir en "Este equipo", **quitar "- Acceso directo"** |
| Escritorio e iconos | Mostrar/ocultar Este equipo, Usuario, Red, Panel de control, Papelera y el icono de Spotlight |
| Pantalla de bloqueo | Quitar curiosidades/anuncios, desactivar pantalla de bloqueo*, quitar el desenfoque del login* |

### ⚙️ Optimización

| Categoría | Ejemplos |
|-----------|----------|
| Rendimiento | Plan de alto rendimiento*, efectos visuales a rendimiento, sin animaciones, menús instantáneos, sin aceleración del ratón, Power Throttling*, **apps en segundo plano** |
| Arranque y apagado | Desactivar inicio rápido*, hibernación*, sonido de arranque*, animación de bienvenida*, mensajes detallados* |
| Privacidad y telemetría | Contenido sugerido, telemetría*, **Windows Recall (IA)**, búsqueda web*, **servicio DiagTrack***, apps promocionadas*, Spotlight* |
| Red | Liberar ancho de banda QoS*, desactivar descargas P2P*, NetworkThrottlingIndex*, **desactivar el algoritmo de Nagle*** |
| Juegos | Game DVR, HAGS*, prioridad del sistema*, optimizaciones de pantalla completa, aviso de teclas especiales, **⚠ desactivar VBS/HVCI*** |
| Sistema | Rutas largas*, NTFS sin "último acceso"*, servicio SysMain*, almacenamiento reservado*, **⚠ reducir UAC***, **⚠ SmartScreen*** |

\* Requieren ejecutar la app como administrador (los del candado 🔒).
⚠ Reducen la seguridad: la app pide confirmación antes de activarlos.

> Algunos ajustes (marcados con ♻️ en la app) requieren **reiniciar el PC** para
> aplicarse; el resto son inmediatos o solo necesitan **reiniciar el Explorador**
> (botón 🔄 en la barra superior).

## Cómo funciona

- Los cambios **se aplican al instante** al mover el interruptor.
- Cada interruptor refleja el **estado actual real** leído del Registro al abrir.
- Para volver a un ajuste a su valor por defecto, simplemente **apágalo de nuevo**:
  la app restaura el valor predeterminado de Windows (o borra la clave/valor).
- Algunos cambios visuales (barra de tareas, Explorador) necesitan
  **reiniciar el Explorador** — usa el botón "🔄 Reiniciar Explorador".

## Estructura del código

| Archivo | Descripción |
|---------|-------------|
| `registry_utils.py` | Lectura/escritura/borrado seguro del Registro (vista de 64 bits) |
| `tweaks_data.py` | Catálogo de ajustes: claves, valores y descripciones |
| `main.py` | Interfaz gráfica (CustomTkinter) |

Para **añadir un ajuste nuevo** solo tienes que agregar un objeto `Tweak` a la
lista `TWEAKS` en `tweaks_data.py`; la interfaz lo mostrará automáticamente.

## Generar un .exe independiente

Para distribuir REPTOSX sin que el usuario tenga Python:

- **Doble clic en `construir_exe.bat`** → genera `dist\REPTOSX.exe`, un único
  ejecutable que incluye todo. Al abrirlo, Windows pedirá permisos de
  administrador (así funcionan también los ajustes del sistema).

El script ya configura `--collect-all customtkinter` (recursos de la interfaz),
`--onefile`, `--windowed` y `--uac-admin`. Si colocas un `REPTOSX.ico` en la
carpeta, lo usará como icono del ejecutable automáticamente.

> Nota: SmartScreen puede avisar de "editor desconocido" porque el .exe no está
> firmado digitalmente; es normal en ejecutables de PyInstaller sin firma.

## ⚠️ Aviso

Modifica el Registro de Windows. Todos los ajustes incluidos son reversibles
desde la propia app, pero es buena idea crear un **punto de restauración** antes
de hacer cambios masivos en la sección "Sistema".
