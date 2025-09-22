@echo off
cd /d %~dp0
echo ========================================
echo    Iniciando Amoblarte App
echo ========================================
echo.

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Inicializando base de datos...
python init_flask_db.py
if errorlevel 1 (
    echo Error: No se pudo inicializar la base de datos
    pause
    exit /b 1
)

echo.
echo Iniciando aplicacion web...
echo Abre tu navegador en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener la aplicacion
echo.

python app.py
