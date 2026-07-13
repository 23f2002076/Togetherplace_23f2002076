@echo off
echo ===================================================
echo   Starting Placement Portal Application (PPA-V2)
echo ===================================================

echo.
echo [1/4] Starting Redis via WSL (Windows Subsystem for Linux)...
wsl -e sudo service redis-server start >nul 2>&1
wsl -e redis-server --daemonize yes >nul 2>&1

echo [2/4] Opening new window for Celery Worker...
start "Celery Worker" cmd /k "cd backend && .\venv\Scripts\activate && celery -A celery_worker.celery worker --loglevel=info --pool=solo"

echo [3/4] Opening new window for Celery Beat (Scheduler)...
start "Celery Beat" cmd /k "cd backend && .\venv\Scripts\activate && celery -A celery_worker.celery beat --loglevel=info"

echo [4/4] Starting Flask Web Server...
echo.
echo The app will be available at http://localhost:5001
echo Press Ctrl+C in this window to stop the web server.
echo.

cd backend
call .\venv\Scripts\activate
python app.py
