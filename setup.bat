@echo off
chcp 65001 >nul
echo ============================================================
echo   CASAC - Sistema de Preparacion al Examen de Frances
echo   Configuracion para Windows
echo ============================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo Descargalo desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

echo [1/4] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

echo [2/4] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo [4/4] Verificando archivo .env...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo Archivo .env creado desde .env.example.
        echo IMPORTANTE: Edita el archivo .env y agrega tu ANTHROPIC_API_KEY.
    ) else (
        echo IMPORTANTE: Crea un archivo .env con tu ANTHROPIC_API_KEY.
    )
) else (
    echo Archivo .env ya existe.
)

echo.
echo ============================================================
echo   Instalacion completada correctamente.
echo   Ejecuta "run.bat" para iniciar el sistema.
echo ============================================================
pause
