@echo off
REM Lanzador de REPTOSX - Herramienta para Windows 11. Doble clic para abrir.
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Si ves un error, instala las dependencias con:
    echo     pip install customtkinter
    pause
)
