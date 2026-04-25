# CASAC - Setup para Windows (PowerShell)
# Si la ejecucion esta bloqueada, ejecuta primero:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  CASAC - Sistema de Preparacion al Examen de Frances" -ForegroundColor Cyan
Write-Host "  Configuracion para Windows (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion encontrado." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no esta instalado o no esta en el PATH." -ForegroundColor Red
    Write-Host "Descargalo desde https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Crear entorno virtual
Write-Host "[1/4] Creando entorno virtual..."
python -m venv venv

# Activar entorno virtual
Write-Host "[2/4] Activando entorno virtual..."
& ".\venv\Scripts\Activate.ps1"

# Instalar dependencias
Write-Host "[3/4] Instalando dependencias..."
pip install -r requirements.txt

# Verificar .env
Write-Host "[4/4] Verificando archivo .env..."
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Archivo .env creado desde .env.example." -ForegroundColor Yellow
        Write-Host "IMPORTANTE: Edita .env y agrega tu ANTHROPIC_API_KEY." -ForegroundColor Yellow
    } else {
        Write-Host "IMPORTANTE: Crea un archivo .env con tu ANTHROPIC_API_KEY." -ForegroundColor Yellow
    }
} else {
    Write-Host "Archivo .env ya existe." -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Instalacion completada. Ejecuta: python main.py" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
