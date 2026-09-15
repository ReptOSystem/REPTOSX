# REPTOSX

Herramienta de personalización y optimización para Windows 11. Permite activar
o desactivar, desde una interfaz gráfica, los ajustes del Registro que
normalmente se modifican a mano con `regedit`.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![UI](https://img.shields.io/badge/UI-CustomTkinter-2563eb)

Creada por reptOSystem. Canal de personalización y optimización de Windows:
<https://www.youtube.com/@reptOSystem>

## Descarga

1. Ve a la sección [Releases](https://github.com/ReptOSystem/REPTOSX/releases) de este repositorio.
2. Descarga `REPTOSX.exe` de la última versión.
3. Ábrelo con doble clic.

No hace falta instalar Python ni ninguna otra dependencia. Al abrirlo, Windows
pedirá permiso de administrador (UAC), necesario para aplicar los ajustes
marcados con el icono de candado. Si SmartScreen avisa de "editor
desconocido", es el comportamiento normal para una aplicación nueva sin firma
digital; puede continuarse desde "Más información → Ejecutar de todas formas".

## Presets

La sección Presets permite aplicar varios ajustes a la vez con un clic:

- **Gaming**: prioridad de la aplicación en primer plano, aceleración de GPU
  por hardware, ajustes de red para reducir latencia y desactivación de
  telemetría y tareas de fondo.
- **Privacidad máxima**: reduce telemetría, sugerencias, Windows Recall,
  búsqueda web y el seguimiento de escritura al mínimo permitido.
- **Escritorio minimalista**: modo oscuro completo y una interfaz más
  despejada, sin widgets, sugerencias ni accesos innecesarios.
- **Limpio y rápido**: elimina bloatware y sugerencias sin tocar la
  privacidad en profundidad.

Antes de aplicar un preset, o de restaurar una categoría entera, la aplicación
muestra cuántos ajustes van a cambiar y avisa si alguno de ellos reduce la
seguridad del sistema. Cada categoría tiene también un botón para restaurar
únicamente sus ajustes a los valores predeterminados.

## Exportar e importar configuración

Desde la sección Presets se puede exportar la configuración activa a un
archivo `.json`, y volver a importarla más adelante (por ejemplo tras
reinstalar Windows, o para compartir una configuración recomendada).

## Información del equipo

La sección Mi equipo muestra el procesador, la memoria RAM en uso, la tarjeta
gráfica con su VRAM, el espacio y tipo de los discos (SSD o HDD) y la versión
de Windows instalada. Toda esta información se lee localmente; no se envía a
ningún sitio.

## Otras funciones

- Tres temas visuales: Oscuro, Claro y Cherry Blossom, con la interfaz
  traducida al español e inglés desde el propio desplegable de idioma.
- Ventana de tamaño proporcional a la pantalla, para verse correctamente
  tanto en portátiles pequeños como en monitores grandes.
- Creación de un punto de restauración del sistema con un clic.
- Búsqueda de ajustes por nombre o descripción.

## Catálogo de ajustes

El catálogo incluye 83 ajustes, priorizando aquellos que no están disponibles
fácilmente desde la propia Configuración de Windows.

### Personalización

| Categoría | Ejemplos |
|---|---|
| Apariencia | Modo oscuro en apps/sistema, calidad máxima del fondo de pantalla, desactivar Aero Shake |
| Barra de tareas | Alinear a la izquierda, ocultar Vista de tareas o búsqueda, no combinar botones, mostrar todos los iconos de la bandeja |
| Menú Inicio | Quitar Bing, más anclajes, no mostrar recientes, desactivar Copilot |
| Explorador | Mostrar extensiones y ocultos, menú contextual clásico, abrir CMD/PowerShell en la carpeta actual |
| Escritorio e iconos | Mostrar u ocultar Este equipo, Red, Panel de control y Papelera |
| Pantalla de bloqueo | Quitar anuncios y curiosidades, desactivar la pantalla de bloqueo* |

### Optimización

| Categoría | Ejemplos |
|---|---|
| Rendimiento | Plan de alto rendimiento*, sin animaciones, sin aceleración del ratón |
| Arranque y apagado | Inicio rápido*, hibernación*, sonido y animación de bienvenida* |
| Privacidad y telemetría | Telemetría*, Windows Recall, búsqueda web*, servicio DiagTrack* |
| Red | Ancho de banda reservado (QoS)*, descargas P2P*, algoritmo de Nagle* |
| Juegos | Game DVR, aceleración de GPU por hardware*, prioridad del sistema* |
| Sistema | Rutas largas*, servicio SysMain*, almacenamiento reservado*, reducir UAC* |

\* Requiere ejecutar la aplicación como administrador.

Los ajustes que reducen la seguridad del sistema están marcados en la interfaz
y piden confirmación antes de activarse. Algunos cambios requieren reiniciar
el Explorador o el equipo para aplicarse por completo.

## Funcionamiento

Los cambios se aplican de inmediato al mover un interruptor, y cada uno
refleja el estado real leído del Registro. Desactivar un ajuste lo devuelve a
su valor predeterminado de Windows.

## Aviso

REPTOSX modifica el Registro de Windows. Todos los ajustes son reversibles
desde la propia aplicación, pero se recomienda crear un punto de restauración
antes de aplicar varios cambios a la vez, especialmente en la categoría
Sistema.
