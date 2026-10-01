@echo off
setlocal
cd /d "%~dp0"
set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo Could not find the project Python environment at .venv\Scripts\python.exe
  echo Open a terminal in this folder and run: python -m venv .venv
  echo Then install requirements with: .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)
"%PYTHON%" manage.py migrate
if errorlevel 1 goto :startup_error
"%PYTHON%" manage.py seed_products
if errorlevel 1 goto :startup_error
echo.
echo Haven is starting. Open http://127.0.0.1:8000/ in your browser.
"%PYTHON%" manage.py runserver 127.0.0.1:8000
exit /b %errorlevel%

:startup_error
echo.
echo Haven could not start. Review the error above, then try again.
pause
exit /b 1