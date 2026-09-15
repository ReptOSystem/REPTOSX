@echo off
REM ============================================================
REM  Genera REPTOSX.exe (un unico ejecutable independiente).
REM  Doble clic para construir. El .exe queda en la carpeta dist\
REM ============================================================
cd /d "%~dp0"
echo.
echo  ========================================
echo   Construyendo REPTOSX.exe ...
echo  ========================================
echo.

REM 1) Asegura que PyInstaller esta instalado
python -m pip install --upgrade pyinstaller customtkinter
if errorlevel 1 (
    echo.
    echo  [ERROR] No se pudo instalar PyInstaller. Revisa que Python este instalado.
    pause
    exit /b 1
)

REM 2) Si existe un icono REPTOSX.ico se usa; si no, se omite
set ICON=
if exist "REPTOSX.ico" set ICON=--icon REPTOSX.ico

REM 3) Construccion:
REM    --onefile          un solo .exe
REM    --windowed         sin consola negra detras
REM    --uac-admin        pide permisos de administrador al abrir
REM    --collect-all customtkinter   incluye los temas/recursos (imprescindible)
REM    --name REPTOSX     nombre del ejecutable
python -m PyInstaller --onefile --windowed --uac-admin ^
    --collect-all customtkinter ^
    --name REPTOSX %ICON% ^
    main.py

if errorlevel 1 (
    echo.
    echo  [ERROR] La construccion fallo. Revisa los mensajes de arriba.
    pause
    exit /b 1
)

REM 4) Copia el icono junto al .exe: la app lo busca ahi en tiempo de
REM    ejecucion (window.iconbitmap) para la barra de titulo/Alt+Tab.
REM    --icon solo incrusta el icono del ARCHIVO .exe, no basta por si solo.
if exist "REPTOSX.ico" copy /y "REPTOSX.ico" "dist\REPTOSX.ico" >nul

echo.
echo  ========================================
echo   LISTO. El ejecutable esta en:
echo      %~dp0dist\REPTOSX.exe
echo  ========================================
echo.
echo  Nota: al abrir REPTOSX.exe, Windows pedira permiso de administrador (UAC).
echo.
pause
