@echo off
title Historial Clinico Dental
cd /d "%~dp0"

echo Iniciando Historial Clinico Dental...
echo.

:: Verificar que Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo.
    echo Por favor instala Python desde: https://www.python.org/downloads
    echo Asegurate de tildar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b
)

:: Instalar dependencias si faltan
echo Verificando dependencias...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo Instalando libreria de diseño, esto puede tardar un momento...
    pip install customtkinter
)

:: Crear acceso directo en el escritorio la primera vez
set SHORTCUT=%USERPROFILE%\Desktop\Historial Clinico Dental.lnk
if not exist "%SHORTCUT%" (
    echo Creando acceso directo en el escritorio...
    powershell -Command ^
        "$ws = New-Object -ComObject WScript.Shell;" ^
        "$s = $ws.CreateShortcut('%SHORTCUT%');" ^
        "$s.TargetPath = 'pythonw.exe';" ^
        "$s.Arguments = '\""%~dp0main.py\"';" ^
        "$s.WorkingDirectory = '%~dp0';" ^
        "$s.Description = 'Historial Clinico Dental';" ^
        "$s.Save()"
    echo Acceso directo creado. La proxima vez usa el icono del escritorio.
    echo.
)

:: Iniciar la app (sin ventana de consola)
start pythonw main.py
