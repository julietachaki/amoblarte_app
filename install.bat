@echo off
cd /d %~dp0
echo ========================================
echo    Instalador de Amoblarte App
echo ========================================
echo.

echo Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo Error: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Instalacion completada exitosamente
echo ========================================
echo.
echo Para ejecutar la aplicacion:
echo 1. Ejecuta: run.bat
echo 2. O ejecuta: python app.py
echo 3. Abre tu navegador en: http://localhost:5000
echo.
pause
