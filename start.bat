@echo off
setlocal
chcp 65001 > nul
title AWS Builder ID Autoreg

cd /d "%~dp0"

echo.
echo ============================================================
echo    AWS Builder ID Autoreg - installer and menu
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found in PATH.
    echo     Install Python 3.10+ from https://python.org/downloads
    echo     IMPORTANT: tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

if not exist ".deps_installed" (
    echo [i] Installing dependencies, please wait...
    echo.
    python -m pip install --upgrade pip
    if errorlevel 1 goto :deps_fail
    python -m pip install -r requirements.txt
    if errorlevel 1 goto :deps_fail
    python -m pip install --upgrade undetected-chromedriver
    if errorlevel 1 goto :deps_fail
    python -m pip install --upgrade selenium
    if errorlevel 1 goto :deps_fail
    python -m pip install --upgrade requests pyyaml
    if errorlevel 1 goto :deps_fail
    echo done > .deps_installed
    echo.
    echo [OK] Dependencies installed.
    echo.
)

echo [i] Syncing version_main with Chrome...
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\sync_chrome_version.ps1"

echo.
echo [i] Starting menu...
echo.
python menu.py

echo.
pause
exit /b 0

:deps_fail
echo.
echo [X] Dependency install failed. Check error above.
pause
exit /b 1
