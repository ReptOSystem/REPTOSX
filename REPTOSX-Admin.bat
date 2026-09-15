@echo off
REM Lanza REPTOSX con privilegios de administrador (necesario para ajustes del sistema).
cd /d "%~dp0"
powershell -Command "Start-Process python -ArgumentList 'main.py' -WorkingDirectory '%~dp0' -Verb RunAs"
