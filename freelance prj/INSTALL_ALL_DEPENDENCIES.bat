@echo off
color 0A
title Social Media Comment Analyzer - Install All Dependencies
cls

echo =============================================================
echo   SOCIAL MEDIA COMMENT ANALYZER - INSTALLATION
echo =============================================================
echo.
echo This will install everything needed to run the application.
echo Please wait...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js 14+ from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo [OK] Node.js found

echo.
echo Installing Python modules (backend)...
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python modules!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo [OK] Python modules installed
cd ..

echo.
echo Installing Node.js modules (frontend)...
cd frontend
npm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node.js modules!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo [OK] Node.js modules installed
cd ..

echo.
echo =============================================================
echo   ALL DEPENDENCIES INSTALLED SUCCESSFULLY!
echo =============================================================
echo You can now double-click START_APP.bat or START_APPLICATION.bat to run the application.
echo.
pause
