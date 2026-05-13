@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   AWS Builder ID — Авторегистратор
echo ========================================
echo.
echo Установка зависимостей...
pip install -r requirements.txt -q
echo.
echo Запуск...
python src\runners\main.py
pause