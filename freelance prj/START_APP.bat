@echo off
echo ====================================
echo Instagram Comment Analyzer
echo ====================================
echo.

echo Starting Backend Server...
cd /d "%~dp0backend"

start "Instagram Analyzer Backend" python app.py

timeout /t 3 /nobreak >nul

echo.
echo Backend started at: http://localhost:5000
echo.
echo Opening Frontend...
timeout /t 2 /nobreak >nul

cd /d "%~dp0frontend"
start index.html

echo.
echo ====================================
echo Application Started!
echo ====================================
echo.
echo Backend: http://localhost:5000
echo Frontend: Opened in your browser
echo.
echo Press any key to stop the backend...
pause >nul

taskkill /FI "WINDOWTITLE eq Instagram Analyzer Backend*" /F >nul 2>&1
echo Backend stopped.
