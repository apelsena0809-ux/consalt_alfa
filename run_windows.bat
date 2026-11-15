@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Не найдено виртуальное окружение .venv.
    echo Сначала выполните команды установки из README_UI.md.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m streamlit run app.py

pause
