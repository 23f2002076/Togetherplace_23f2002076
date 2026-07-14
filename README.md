# Placement Portal Application (PPA-V2)

## How to Run Locally

You will need to open 4 separate terminal windows to run all components of this application locally on Windows.

### Terminal 1: Redis Server (Database Cache)
*Since Redis runs natively on Linux, use WSL to start it in the background.*
```powershell
wsl -e sudo service redis-server start
wsl -e redis-server --daemonize yes
```

### Terminal 2: Web Server (Flask + Vue)
*This runs the main website backend and serves the frontend.*
```powershell
cd backend
.\venv\Scripts\activate
python app.py
```
*Once running, open your browser and go to **http://localhost:5001**.*

### Terminal 3: Celery Worker (Heavy Background Tasks)
*This handles generating CSV exports and sending emails.*
```powershell
cd backend
.\venv\Scripts\activate
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

### Terminal 4: Celery Beat (Time-based Scheduler)
*This triggers periodic tasks like your daily reminders.*
```powershell
cd backend
.\venv\Scripts\activate
celery -A celery_worker.celery beat --loglevel=info
```