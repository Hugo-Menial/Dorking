@echo off
title Dorking Tool — OSINT & Security Research
cd /d "%~dp0"

echo ============================================
echo   DORKING TOOL — OSINT ^& Security Research
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH.
    pause
    exit /b 1
)

echo Verification des dependances...
pip install -r requirements.txt -q

echo.
echo Lancement de l'application...
python main.py

if errorlevel 1 (
    echo.
    echo ERREUR: L'application a rencontre un probleme.
    pause
)
