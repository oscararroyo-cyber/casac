@echo off
chcp 65001 >nul

if not exist venv (
    echo Entorno virtual no encontrado. Ejecuta setup.bat primero.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python bot.py
