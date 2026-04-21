@echo off
title Installation — Dorking Tool
cd /d "%~dp0"

echo ============================================
echo   INSTALLATION — DORKING TOOL
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas detecte. Installez Python 3.11+ depuis python.org
    pause
    exit /b 1
)

echo Installation des dependances Python...
pip install -r requirements.txt

echo.
echo ============================================
echo   Installation terminee !
echo   Lancez l'application avec : lancer.bat
echo ============================================
pause
